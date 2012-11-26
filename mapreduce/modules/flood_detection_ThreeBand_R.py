import numpy
import time

import sys

class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr
  
    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

rpy2.robjects.numpy2ri.activate()

import json
import GeoPictureSerializer

def newBand(geoPicture, classificationType=1, dataType=1):
  with RedirectStdStreams(stdout=sys.stderr, stderr=sys.stderr):

    #load the image into an array
    imageArray = geoPicture.picture

    #create a list of bands array
    presentBands = geoPicture.bands

    #create a numerical vector corresponding to bands present
    presentBandsNum = numpy.zeros(len(presentBands), dtype=numpy.uint8)
    for i in numpy.arange(len(presentBands)):
        presentBandsNum[i] = int( presentBands[i].lstrip('B') )

    #load metadata
    l1t = json.loads(geoPicture.metadata["L1T"])

    if l1t["PRODUCT_METADATA"]["SENSOR_ID"] == "HYPERION":
        imageArray = hypSolarIrradiance(imageArray, presentBandsNum)
        imageArray, presentBands = binBands(imageArray, presentBandsNum)

        #create new presentBandsNum vector
        presentBandsNum = numpy.zeros(len(presentBands), dtype=numpy.uint8)
        for i in numpy.arange(len(presentBands)):
            presentBandsNum[i] = int( presentBands[i].lstrip('B') )

    else:
        imageArray = rescaleALI(l1t, imageArray, presentBandsNum)
        imageArray = aliSolarIrradiance(imageArray, presentBandsNum)

    #geometric correction
    imageArray = geometricCorrection(imageArray, l1t)

    #Find size of the image array 
    rasterXsize = imageArray.shape[1]
    rasterYsize = imageArray.shape[0]
    rasterDepth = imageArray.shape[2]

    x = numpy.linspace(0, rasterXsize-1, rasterXsize)
    y = numpy.linspace(0, rasterYsize-1, rasterYsize)

    nx , ny = numpy.meshgrid(x, y)
    colIndex = nx.reshape(nx.size,1)  #These are intentionally flipped because arrays are indexed [y,x], or [row, column].
    rowIndex = ny.reshape(ny.size,1)
    rcIndex = numpy.concatenate((rowIndex,colIndex),axis=1)

    #Reshape all arrays
    imageArray = imageArray.reshape(rasterXsize*rasterYsize,1,rasterDepth)
    imageArray = imageArray.sum(1) 

    #Need to create a mask of locations where all pixels are nonzero.
    alphaBand = (imageArray[:,presentBands.index(presentBands[0])] > 0)
    for band in presentBands[1:]:
        numpy.logical_and(alphaBand, imageArray[:,presentBands.index(band)], alphaBand)

    #apply mask to image array and index array 
    imageArray = imageArray[alphaBand,:]
    rcIndex = rcIndex[alphaBand,:]

    #Concatenate array
    imageArray = numpy.concatenate((rcIndex, imageArray), axis=1)

    #move some data to R
    #trainingSet
    training = numpy.loadtxt('trainingSet.txt')
    trainingSet = training[:,presentBandsNum-2]
    if dataType==2:
        trainingSet_ratio = numpy.zeros((trainingSet.shape[0],presentBandsNum.size*(presentBandsNum.size-1)/2))
        ij = -1
        for i in numpy.arange(trainingSet.shape[1]-1):
            for j in numpy.arange(i+1,trainingSet.shape[1]):
                ij = ij+1
                trainingSet_ratio[:,ij] = trainingSet[:,i] / trainingSet[:,j]
        trainingSet = trainingSet_ratio
    trainingSet = numpy.concatenate((trainingSet,training[:,-1:]),axis=1)
    robjects.r.assign('trainingSet',trainingSet)
    robjects.r('trainingSet <- as.data.frame(trainingSet)')


    #construct classifier from training data
    if classificationType==1:
        print('using SVM as classifier')
        robjects.r.library("e1071")
        robjects.r('class.model <- svm(V' + str(trainingSet.shape[1]) + ' ~ ., data = trainingSet, type = "C", cost = 1000, kernel = "linear")')
    elif classificationType==2:
        print('using Naive Bayes as classifier')
        robjects.r.library("e1071")
        robjects.r('class.model <- naiveBayes(V' + str(trainingSet.shape[1]) + ' ~ ., data = trainingSet)')
    else:
        robjects.r.library("rpart")
        robjects.r('class.model <- rpart(V' + str(trainingSet.shape[1]) + ' ~ ., method = "class", data = trainingSet)')

    #classify this image 1=cloud, 2=land(desert), 3=water, 4=land(vegetation)
    if dataType==2:
        print('using ratios to classify')
        imgArray1 = numpy.zeros((imageArray.shape[0],presentBandsNum.size*(presentBandsNum.size-1)/2))
        ij = -1
        for i in numpy.arange(2,imageArray.shape[1]-1):
            for j in numpy.arange(i+1,imageArray.shape[1]):
                ij = ij+1
                imgArray1[:,ij] = imageArray[:,i] / imageArray[:,j]
        classVector = classify(imgArray1, presentBandsNum, classificationType)
    else:
        classVector = classify(imageArray[:,2:], presentBandsNum, classificationType)
#

    #Enumerate the classes contained in this vector
    U, Uindices = numpy.unique(classVector, return_inverse=True)

    #Create a rectangular array into which the parallelogram will be placed
    imageArrayFinal = numpy.zeros((geoPicture.picture.shape[0],geoPicture.picture.shape[1],max(U.size,3)), dtype=numpy.float)
    for i in numpy.arange(imageArray.shape[0]):
        imageArrayFinal[imageArray[i,0],imageArray[i,1],Uindices[i]] = 1./ classVector[i]

    for i in numpy.arange(3,U.size):                                               #any band index 3 or above 
        imageArrayFinal[:,:,1] = imageArrayFinal[:,:,1] + imageArrayFinal[:,:,i]   #(corresponding to class label 4 or above), 
                                                                                   #is placed into "land" band, i.e., green band,
                                                                                   # which is python index 1.                                                                               
                                                                                   #since bands are never non-zero in same location, 
                                                                                   #summing compresses multiple bands into one, 
                                                                                   #without losing information.

    imageArrayFinal = numpy.array(imageArrayFinal[:,:,0:3] * numpy.array( [[[1.,2.,3.]]] ),dtype=numpy.float)

    geoPicture.bands.extend(["CLOUDS","LAND","WATER"])

    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = geoPicture.bands
    geoPictureOutput.picture = numpy.concatenate( (geoPicture.picture, imageArrayFinal), axis=2 )
    return geoPictureOutput


def classify(imgArray, availableBandsNum, classType):
    #ship image array into R
    robjects.r.assign('testData',imgArray)
    robjects.r('testData <- as.data.frame(testData)')
    if classType==3:
        classPredict = robjects.r('class.predict <- predict(class.model,testData,type="class")')
    elif classType==2:
        robjects.r('class.predict <- predict(class.model,testData,type="raw")')
        m = imgArray.shape[0]
        robjects.r( 'n <- dim(trainingSet)[2]' )
        robjects.r('classMatrix <- matrix( seq(1, length(unique(trainingSet[ ,n])), length = length(unique(trainingSet[ ,n]))),' + str(m) + ',length(unique(trainingSet[ ,n])), byrow=T)')
        classPredict = robjects.r('class.predict <- apply(classMatrix*round(class.predict),1,sum)')
    else:
        classPredict = robjects.r('class.predict <- predict(class.model,testData)')
    #process class prediction
    classVector = numpy.asarray( tuple(classPredict) ) 
    if numpy.not_equal(classType,2):
        classPredict = numpy.asarray(tuple(classPredict.levels))[classVector-1]
        classPredict = map(int, classPredict)
    classVector = numpy.reshape(classPredict,(imgArray.shape[0],1))
    return classVector


def binBands(imgArray, availableBandsNum):
    #This function is used to take a HYPERION image with the required bands
    #and average the radiance of those bands to create 9 bands which correspond 
    #to the wavelengths of ALI bands.   

    #all possible ALI bands
    possibleBands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10']

    #These are the numbers of the Ali-equivalent Hyperion band limits.
    hypBandsNum = numpy.array([[11,12,13,14,15,16],                         
                [9,10],
                [18,19,20,21,22,23,24,25],                      
                [28,29,30,31,32,33],
                [42,43,44,45],
                [49,50,51,52,53],
                [106,107,108,109,110,111,112,113,114,115],
                [141,142,143,144,145,146,147,148,149,150,
                 151,152,153,154,155,156,157,158,159,160], 
                [193,194,195,196,197,198,199,200,201,202,
                 203,204,205,206,207,208,209,210,211,212,
                             213,214,215,216,217,218,219]])

   
    hypBands = numpy.zeros(9)
    bandsPresent = []
    finalImage = numpy.zeros( (imgArray.shape[0],imgArray.shape[1],1), dtype=numpy.float )
    for i in numpy.arange(9):
        finalArray = numpy.zeros((imgArray.shape[0],imgArray.shape[1],1), dtype=numpy.float)
        for band in hypBandsNum[i]:
            if (band==availableBandsNum).any():
                finalArray[:,:,0] =  finalArray[:,:,0] + imgArray[:,:,list(availableBandsNum).index(band)]
                bandsPresent.append(possibleBands[i])
                hypBands[i] = hypBands[i] + 1
        finalImage = numpy.concatenate( (finalImage,finalArray), axis=2)
        if hypBands[i] > 0:
            finalImage[:,:,i+1] = finalImage[:,:,i+1] / hypBands[i] #the "+1" is because the first band is a place holder

    finalImage = finalImage[:,:,1:]
    bandsPresent = numpy.unique(bandsPresent)
    bandsPresent = list(bandsPresent) 
    return finalImage, bandsPresent


def rescaleALI(metaData, imgArray, availableBandsNum):

    #Rescale ALI image data
    radianceScaling = metaData['RADIANCE_SCALING']
    bandScaling = numpy.zeros((1,1,availableBandsNum.size))
    bandOffset = numpy.zeros((1,1,availableBandsNum.size))

    for i in numpy.arange(availableBandsNum.size):
        bandScaling[0,0,i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_SCALING_FACTOR'])
        bandOffset[0,0,i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_OFFSET'])

    #scaling and offset
    return (imgArray * 30. * bandScaling) + bandOffset


def geometricCorrection(imgArray, metaData):
    earthSunDistance = numpy.array([[1,.9832], [15,.9836], [32,.9853], [46,.9878], [60,.9909],
                                    [74, .9945], [91, .9993], [106, 1.0033], [121, 1.0076], [135, 1.0109],
                                    [152, 1.0140], [166, 1.0158], [182, 1.0167], [196, 1.0165], [213, 1.0149],
                                    [227, 1.0128], [242, 1.0092], [258, 1.0057], [274, 1.0011], [288, .9972],
                                    [305, .9925], [319, .9892], [335, .9860], [349, .9843], [365, .9833],[366, .9832375]])
    
    julianDate = time.strptime(metaData["PRODUCT_METADATA"]["START_TIME"], "%Y %j %H:%M:%S").tm_yday
    eSD = numpy.interp( numpy.linspace(1,366,366), earthSunDistance[:,0], earthSunDistance[:,1] )
    esDist = eSD[julianDate-1]
    
    sunAngle = float(metaData["PRODUCT_PARAMETERS"]["SUN_ELEVATION"])
    sunAngle = sunAngle*numpy.pi/180.
    imgArray = numpy.pi * esDist**2 * imgArray / numpy.sin(sunAngle)
    return imgArray


def aliSolarIrradiance(imgArray, availableBandsNum):
    Esun_ali = numpy.array([ [2,1851.8], [3, 1967.6], [4, 1837.2], [5,1551.47], [6, 1164.53], [7,957.46], [8, 451.37], [9, 230.03], [10, 79.61] ])
    imgArray = imgArray / numpy.reshape(Esun_ali[availableBandsNum-2,1],(1,1,availableBandsNum.size))
    return imgArray

def hypSolarIrradiance(imgArray, availableBandsNum):
    Esun_hyp = numpy.array([
        [  1.00000000e+00,   9.49370000e+02],
        [  2.00000000e+00,   1.15878000e+03],
        [  3.00000000e+00,   1.06125000e+03],
        [  4.00000000e+00,   9.55120000e+02],
        [  5.00000000e+00,   9.70870000e+02],
        [  6.00000000e+00,   1.66373000e+03],
        [  7.00000000e+00,   1.72292000e+03],
        [  8.00000000e+00,   1.65052000e+03],
        [  9.00000000e+00,   1.71490000e+03],
        [  1.00000000e+01,   1.99452000e+03],
        [  1.10000000e+01,   2.03472000e+03],
        [  1.20000000e+01,   1.97012000e+03],
        [  1.30000000e+01,   2.03622000e+03],
        [  1.40000000e+01,   1.86024000e+03],
        [  1.50000000e+01,   1.95329000e+03],
        [  1.60000000e+01,   1.95355000e+03],
        [  1.70000000e+01,   1.80456000e+03],
        [  1.80000000e+01,   1.90551000e+03],
        [  1.90000000e+01,   1.87750000e+03],
        [  2.00000000e+01,   1.88351000e+03],
        [  2.10000000e+01,   1.82199000e+03],
        [  2.20000000e+01,   1.84192000e+03],
        [  2.30000000e+01,   1.84751000e+03],
        [  2.40000000e+01,   1.77999000e+03],
        [  2.50000000e+01,   1.76145000e+03],
        [  2.60000000e+01,   1.74080000e+03],
        [  2.70000000e+01,   1.70888000e+03],
        [  2.80000000e+01,   1.67209000e+03],
        [  2.90000000e+01,   1.63283000e+03],
        [  3.00000000e+01,   1.59192000e+03],
        [  3.10000000e+01,   1.55766000e+03],
        [  3.20000000e+01,   1.52541000e+03],
        [  3.30000000e+01,   1.47093000e+03],
        [  3.40000000e+01,   1.45037000e+03],
        [  3.50000000e+01,   1.39318000e+03],
        [  3.60000000e+01,   1.37275000e+03],
        [  3.70000000e+01,   1.23563000e+03],
        [  3.80000000e+01,   1.26613000e+03],
        [  3.90000000e+01,   1.27902000e+03],
        [  4.00000000e+01,   1.26522000e+03],
        [  4.10000000e+01,   1.23537000e+03],
        [  4.20000000e+01,   1.20229000e+03],
        [  4.30000000e+01,   1.19408000e+03],
        [  4.40000000e+01,   1.14360000e+03],
        [  4.50000000e+01,   1.12816000e+03],
        [  4.60000000e+01,   1.10848000e+03],
        [  4.70000000e+01,   1.06850000e+03],
        [  4.80000000e+01,   1.03970000e+03],
        [  4.90000000e+01,   1.02384000e+03],
        [  5.00000000e+01,   9.38960000e+02],
        [  5.10000000e+01,   9.49970000e+02],
        [  5.20000000e+01,   9.49740000e+02],
        [  5.30000000e+01,   9.29540000e+02],
        [  5.40000000e+01,   9.17320000e+02],
        [  5.50000000e+01,   8.92690000e+02],
        [  5.60000000e+01,   8.77590000e+02],
        [  5.70000000e+01,   8.34600000e+02],
        [  5.80000000e+01,   8.37110000e+02],
        [  5.90000000e+01,   8.14700000e+02],
        [  6.00000000e+01,   7.88040000e+02],
        [  6.10000000e+01,   7.78200000e+02],
        [  6.20000000e+01,   7.64290000e+02],
        [  6.30000000e+01,   7.51280000e+02],
        [  6.40000000e+01,   7.40250000e+02],
        [  6.50000000e+01,   7.10540000e+02],
        [  6.60000000e+01,   7.03560000e+02],
        [  6.70000000e+01,   6.95100000e+02],
        [  6.80000000e+01,   6.76900000e+02],
        [  6.90000000e+01,   6.61900000e+02],
        [  7.00000000e+01,   6.49640000e+02],
        [  7.10000000e+01,   9.64600000e+02],
        [  7.20000000e+01,   9.82060000e+02],
        [  7.30000000e+01,   9.54030000e+02],
        [  7.40000000e+01,   9.31810000e+02],
        [  7.50000000e+01,   9.23350000e+02],
        [  7.60000000e+01,   8.94620000e+02],
        [  7.70000000e+01,   8.76100000e+02],
        [  7.80000000e+01,   8.39340000e+02],
        [  7.90000000e+01,   8.41540000e+02],
        [  8.00000000e+01,   8.10200000e+02],
        [  8.10000000e+01,   8.02220000e+02],
        [  8.20000000e+01,   7.84440000e+02],
        [  8.30000000e+01,   7.72220000e+02],
        [  8.40000000e+01,   7.58600000e+02],
        [  8.50000000e+01,   7.43880000e+02],
        [  8.60000000e+01,   7.21760000e+02],
        [  8.70000000e+01,   7.14260000e+02],
        [  8.80000000e+01,   6.98690000e+02],
        [  8.90000000e+01,   6.82410000e+02],
        [  9.00000000e+01,   6.69610000e+02],
        [  9.10000000e+01,   6.57860000e+02],
        [  9.20000000e+01,   6.43480000e+02],
        [  9.30000000e+01,   6.23130000e+02],
        [  9.40000000e+01,   6.03890000e+02],
        [  9.50000000e+01,   5.82630000e+02],
        [  9.60000000e+01,   5.79580000e+02],
        [  9.70000000e+01,   5.71800000e+02],
        [  9.80000000e+01,   5.62300000e+02],
        [  9.90000000e+01,   5.51400000e+02],
        [  1.00000000e+02,   5.40520000e+02],
        [  1.01000000e+02,   5.34170000e+02],
        [  1.02000000e+02,   5.19740000e+02],
        [  1.03000000e+02,   5.11290000e+02],
        [  1.04000000e+02,   4.97280000e+02],
        [  1.05000000e+02,   4.92820000e+02],
        [  1.06000000e+02,   4.79410000e+02],
        [  1.07000000e+02,   4.79560000e+02],
        [  1.08000000e+02,   4.69010000e+02],
        [  1.09000000e+02,   4.61600000e+02],
        [  1.10000000e+02,   4.51000000e+02],
        [  1.11000000e+02,   4.44060000e+02],
        [  1.12000000e+02,   4.35250000e+02],
        [  1.13000000e+02,   4.29290000e+02],
        [  1.14000000e+02,   4.15690000e+02],
        [  1.15000000e+02,   4.12870000e+02],
        [  1.16000000e+02,   4.05400000e+02],
        [  1.17000000e+02,   3.96940000e+02],
        [  1.18000000e+02,   3.91940000e+02],
        [  1.19000000e+02,   3.86790000e+02],
        [  1.20000000e+02,   3.80650000e+02],
        [  1.21000000e+02,   3.70960000e+02],
        [  1.22000000e+02,   3.65570000e+02],
        [  1.23000000e+02,   3.58420000e+02],
        [  1.24000000e+02,   3.55180000e+02],
        [  1.25000000e+02,   3.49040000e+02],
        [  1.26000000e+02,   3.42100000e+02],
        [  1.27000000e+02,   3.36000000e+02],
        [  1.28000000e+02,   3.25940000e+02],
        [  1.29000000e+02,   3.25710000e+02],
        [  1.30000000e+02,   3.18270000e+02],
        [  1.31000000e+02,   3.12120000e+02],
        [  1.32000000e+02,   3.08080000e+02],
        [  1.33000000e+02,   3.00520000e+02],
        [  1.34000000e+02,   2.92270000e+02],
        [  1.35000000e+02,   2.93280000e+02],
        [  1.36000000e+02,   2.82140000e+02],
        [  1.37000000e+02,   2.85600000e+02],
        [  1.38000000e+02,   2.80410000e+02],
        [  1.39000000e+02,   2.75870000e+02],
        [  1.40000000e+02,   2.71970000e+02],
        [  1.41000000e+02,   2.65730000e+02],
        [  1.42000000e+02,   2.60200000e+02],
        [  1.43000000e+02,   2.51620000e+02],
        [  1.44000000e+02,   2.44110000e+02],
        [  1.45000000e+02,   2.47830000e+02],
        [  1.46000000e+02,   2.42850000e+02],
        [  1.47000000e+02,   2.38150000e+02],
        [  1.48000000e+02,   2.39290000e+02],
        [  1.49000000e+02,   2.27380000e+02],
        [  1.50000000e+02,   2.26690000e+02],
        [  1.51000000e+02,   2.25480000e+02],
        [  1.52000000e+02,   2.18690000e+02],
        [  1.53000000e+02,   2.09070000e+02],
        [  1.54000000e+02,   2.10620000e+02],
        [  1.55000000e+02,   2.06980000e+02],
        [  1.56000000e+02,   2.01590000e+02],
        [  1.57000000e+02,   1.98090000e+02],
        [  1.58000000e+02,   1.91770000e+02],
        [  1.59000000e+02,   1.84020000e+02],
        [  1.60000000e+02,   1.84910000e+02],
        [  1.61000000e+02,   1.82750000e+02],
        [  1.62000000e+02,   1.80090000e+02],
        [  1.63000000e+02,   1.75180000e+02],
        [  1.64000000e+02,   1.73000000e+02],
        [  1.65000000e+02,   1.68870000e+02],
        [  1.66000000e+02,   1.65190000e+02],
        [  1.67000000e+02,   1.56300000e+02],
        [  1.68000000e+02,   1.59010000e+02],
        [  1.69000000e+02,   1.55220000e+02],
        [  1.70000000e+02,   1.52620000e+02],
        [  1.71000000e+02,   1.49140000e+02],
        [  1.72000000e+02,   1.41630000e+02],
        [  1.73000000e+02,   1.39430000e+02],
        [  1.74000000e+02,   1.39220000e+02],
        [  1.75000000e+02,   1.37970000e+02],
        [  1.76000000e+02,   1.36730000e+02],
        [  1.77000000e+02,   1.33960000e+02],
        [  1.78000000e+02,   1.30290000e+02],
        [  1.79000000e+02,   1.24500000e+02],
        [  1.80000000e+02,   1.24750000e+02],
        [  1.81000000e+02,   1.23920000e+02],
        [  1.82000000e+02,   1.21950000e+02],
        [  1.83000000e+02,   1.18960000e+02],
        [  1.84000000e+02,   1.17780000e+02],
        [  1.85000000e+02,   1.15560000e+02],
        [  1.86000000e+02,   1.14520000e+02],
        [  1.87000000e+02,   1.11650000e+02],
        [  1.88000000e+02,   1.09210000e+02],
        [  1.89000000e+02,   1.07690000e+02],
        [  1.90000000e+02,   1.06130000e+02],
        [  1.91000000e+02,   1.03700000e+02],
        [  1.92000000e+02,   1.02420000e+02],
        [  1.93000000e+02,   1.00420000e+02],
        [  1.94000000e+02,   9.82700000e+01],
        [  1.95000000e+02,   9.73700000e+01],
        [  1.96000000e+02,   9.54400000e+01],
        [  1.97000000e+02,   9.35500000e+01],
        [  1.98000000e+02,   9.23500000e+01],
        [  1.99000000e+02,   9.09300000e+01],
        [  2.00000000e+02,   8.93700000e+01],
        [  2.01000000e+02,   8.46400000e+01],
        [  2.02000000e+02,   8.54700000e+01],
        [  2.03000000e+02,   8.44900000e+01],
        [  2.04000000e+02,   8.34300000e+01],
        [  2.05000000e+02,   8.16200000e+01],
        [  2.06000000e+02,   8.06700000e+01],
        [  2.07000000e+02,   7.93200000e+01],
        [  2.08000000e+02,   7.81100000e+01],
        [  2.09000000e+02,   7.66900000e+01],
        [  2.10000000e+02,   7.53500000e+01],
        [  2.11000000e+02,   7.41500000e+01],
        [  2.12000000e+02,   7.32500000e+01],
        [  2.13000000e+02,   7.16700000e+01],
        [  2.14000000e+02,   7.01300000e+01],
        [  2.15000000e+02,   6.95200000e+01],
        [  2.16000000e+02,   6.82800000e+01],
        [  2.17000000e+02,   6.63900000e+01],
        [  2.18000000e+02,   6.57600000e+01],
        [  2.19000000e+02,   6.52300000e+01],
        [  2.20000000e+02,   6.30900000e+01],
        [  2.21000000e+02,   6.29000000e+01],
        [  2.22000000e+02,   6.16800000e+01],
        [  2.23000000e+02,   6.00000000e+01],
        [  2.24000000e+02,   5.99400000e+01],
        [  2.25000000e+02,   5.91800000e+01],
        [  2.26000000e+02,   5.73800000e+01],
        [  2.27000000e+02,   5.71000000e+01],
        [  2.28000000e+02,   5.62500000e+01],
        [  2.29000000e+02,   5.50900000e+01],
        [  2.30000000e+02,   5.40200000e+01],
        [  2.31000000e+02,   5.37500000e+01],
        [  2.32000000e+02,   5.27800000e+01],
        [  2.33000000e+02,   5.16000000e+01],
        [  2.34000000e+02,   5.14400000e+01],
        [  2.35000000e+02,   0.00000000e+00],
        [  2.36000000e+02,   0.00000000e+00],
        [  2.37000000e+02,   0.00000000e+00],
        [  2.38000000e+02,   0.00000000e+00],
        [  2.39000000e+02,   0.00000000e+00],
        [  2.40000000e+02,   0.00000000e+00],
        [  2.41000000e+02,   0.00000000e+00],
        [  2.42000000e+02,   0.00000000e+00]])
    Esun_hyp = Esun_hyp[availableBandsNum,1]
    imgArray = imgArray / numpy.reshape(Esun_hyp,(1,1,Esun_hyp.shape[0]))
    return imgArray
