import numpy

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

rpy2.robjects.numpy2ri.activate()

import json
import GeoPictureSerializer


def newBand(geoPicture):
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
        imageArray, presentBands = binBands(imageArray, presentBandsNum) 
        #create new presentBandsNum vector
        presentBandsNum = numpy.zeros(len(presentBands), dtype=numpy.uint8)
        for i in numpy.arange(len(presentBands)):
            presentBandsNum[i] = int( presentBands[i].lstrip('B') )
    else:
        imageArray = rescaleALI(l1t, imageArray, presentBandsNum)

    #sun angle correction
    imageArray = sunCorrection(imageArray, l1t)

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
    robjects.r('trainingSet <- read.table("trainingSet.txt")')
    #select class column - always column 10 of training set 
    robjects.r('trainingClass <- trainingSet[ ,10]')
    #data columns
    dataColumns = numpy.array(presentBandsNum - 1, dtype=numpy.uint8)
    dataColumnNames = 'c' + str( tuple( dataColumns ) )
    robjects.r('trainingData <- trainingSet[ ,' + dataColumnNames + ']')
    #construct svm from training data
    robjects.r('svm.model <- svm(trainingData, trainingClass, type = "C", kernel = "linear")')

    #classify this image
    classVector = classify(imageArray, presentBandsNum)

    #Create a rectangular array into which the parallelogram will be placed
    imageArrayClass = numpy.zeros((geoPicture.picture.shape[0],geoPicture.picture.shape[1],1), dtype=numpy.uint8)
    for i in numpy.arange(imageArray.shape[0]):
        imageArrayClass[imageArray[i,0],imageArray[i,1],0] = 255. / classVector[i]

    geoPicture.bands.extend(["FLOOD"])

    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = geoPicture.bands
    geoPictureOutput.picture = numpy.concatenate( (geoPicture.picture, imageArrayClass), axis=2 )
    return geoPictureOutput


def classify(imgArray, availableBandsNum):
    #ship image array into R
    robjects.r.assign('testData',imgArray[:,2:])
    #classify image using svm
    svmPredict = robjects.r('svm.predict <- predict(svm.model,testData)')
    #process class prediction
    svmPredict = tuple(svmPredict)
    svmPredict = numpy.asarray(svmPredict)
    classVector = numpy.reshape(svmPredict,(imgArray.shape[0],1))
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
    bandScaling = zeros(len(availableBandsNum))
    bandOffset = zeros(len(availableBandsNum))

    for i in arange(availableBandsNum.size):
        bandScaling[i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_SCALING_FACTOR'])
        bandOffset[i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_OFFSET'])

    #scaling and offset
    imgArray = (imgArray * 300. * bandScaling) + bandOffset


def sunCorrection(imgArray, metaData):
    sunAngle = float(metaData["PRODUCT_PARAMETERS"]["SUN_ELEVATION"])
    sunAngle = sunAngle*numpy.pi/180.
    imgArray = imgArray/numpy.sin(sunAngle)
    return imgArray

