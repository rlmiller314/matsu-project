#!/usr/bin.env python
import numpy

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

rpy2.robjects.numpy2ri.activate()

import json
import GeoPictureSerializer

import os
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

    #classify this image
    imageArray = classify(imageArray, presentBandsNum)

    #Enumerate the classes contained in this vector
    classVector = imageArray[:,imageArray.shape[1]-1]
    U, Uindices = numpy.unique(classVector, return_inverse=True)

    #Create a rectangular array into which the parallelogram will be placed
    imageArrayFinal = numpy.zeros((geoPicture.picture.shape[0],geoPicture.picture.shape[1],U.size), dtype=numpy.uint8)
    for i in numpy.arange(imageArray.shape[0]):
        imageArrayFinal[imageArray[i,0],imageArray[i,1],Uindices[i]] = imageArray[i,imageArray.shape[1]-1]

    for i in numpy.arange(U.size):
        imageArrayFinal[:,:,i] = imageArrayFinal[:,:,i] * 255. / numpy.square(imageArrayFinal[:,:,i].max())

    if U.size > 3:
        imageArrayFinal[:,:,1] = imageArrayFinal[:,:,1] + imageArrayFinal[:,:,3] #Since bands are orthogonally zero, summing combines land bands

    imageArrayFinal = numpy.array(imageArrayFinal[:,:,0:3], dtype=numpy.uint8)  #Compress to 3 bands for RGB image

    imageArrayFinal = numpy.concatenate( (geoPicture.picture, imageArrayFinal), axis=2)

    presentBands.extend(["CLOUD","LAND","WATER"])

    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = presentBands
    geoPictureOutput.picture = imageArrayFinal
    return geoPictureOutput


def classify(imgArray, availableBandsNum):

    with RedirectStdStreams(stdout=sys.stderr, stderr=sys.stderr):
        robjects.r('library("e1071")')

    #trainingSet
    robjects.r('trainingSet <- read.table("trainingSet.txt")')
    #select class column
    robjects.r('trainingClass <- trainingSet[ , 10]')
    #data columns
    dataColumns = numpy.array(availableBandsNum - 1, dtype=numpy.uint8)
    dataColumnNames = 'c' + str( tuple( dataColumns ) )
    robjects.r('trainingData <- trainingSet[ ,' + dataColumnNames + ']')
    #construct svm from training data
    robjects.r('svm.model <- svm(trainingData, trainingClass, type = "C", kernel = "linear")')

    #ship image array into R
    robjects.r.assign('testData',imgArray[:,2:])
    #classify image using svm
    svmPredict = robjects.r('svm.predict <- predict(svm.model,testData)')
    #process class prediction
    svmPredict = tuple(svmPredict)
    svmPredict = numpy.asarray(svmPredict)
    svmPredict = numpy.reshape(svmPredict,(imgArray.shape[0],1))
    #append classification vector to image array
    imgArray = numpy.concatenate( (imgArray,svmPredict), axis=1)
    return imgArray


def binBands(imgArray, availableBandsNum):
    #This function is used to take a HYPERION image with the required bands
    #and average the radiance of those bands to create 9 bands which correspond 
    #to the wavelengths of ALI bands.   

    #These are the numbers of the Ali-equivalent Hyperion band limits.
    hypStartVec = numpy.array([9, 11, 18, 28, 42, 49, 106, 141, 193], dtype=numpy.uint8)
    hypStopVec = numpy.array([10, 16, 25, 33, 45, 53, 115, 160, 219], dtype=numpy.uint8)

    #
    aliStopVec = numpy.zeros(hypStartVec.size, dtype = numpy.int32)
    hypAux = numpy.arange(availableBandsNum.size)
    for i in numpy.arange(hypStartVec.size):
        while (hypStopVec[i]!=availableBandsNum).all():
            hypStopVec[i] -= 1
        aliMask = hypStopVec[i]==availableBandsNum
        aliStopVec[i] = (hypAux[aliMask])[0] + 1

    bandsPresent = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10']
    xsize, ysize, zsize = imgArray.shape

    img3 = imgArray[:,:,0:aliStopVec[0]]
    Img3 = img3.sum(2)/aliStopVec[0]

    img2 = imgArray[:,:,aliStopVec[0]:aliStopVec[1]]
    Img2 = img2.sum(2)/(aliStopVec[1]-aliStopVec[0])

    img4 = imgArray[:,:,aliStopVec[1]:aliStopVec[2]]
    Img4 = img4.sum(2)/(aliStopVec[2]-aliStopVec[1])

    img5 = imgArray[:,:,aliStopVec[2]:aliStopVec[3]]
    Img5 = img5.sum(2)/(aliStopVec[3]-aliStopVec[2])

    img6 = imgArray[:,:,aliStopVec[3]:aliStopVec[4]]
    Img6 = img6.sum(2)/(aliStopVec[4]-aliStopVec[3])

    img7 = imgArray[:,:,aliStopVec[4]:aliStopVec[5]]
    Img7 = img7.sum(2)/(aliStopVec[5]-aliStopVec[4])

    img8 = imgArray[:,:,aliStopVec[5]:aliStopVec[6]]
    Img8 = img8.sum(2)/(aliStopVec[6]-aliStopVec[5])

    img9 = imgArray[:,:,aliStopVec[6]:aliStopVec[7]]
    Img9 = img9.sum(2)/(aliStopVec[7]-aliStopVec[6])

    img10 = imgArray[:,:,aliStopVec[7]:aliStopVec[8]]
    Img10 = img10.sum(2)/(aliStopVec[8]-aliStopVec[7])

    finalImage = numpy.ndarray(shape=[xsize, ysize, 9], dtype = 'float')
    finalImage[:,:,0] = Img2
    finalImage[:,:,1] = Img3
    finalImage[:,:,2] = Img4
    finalImage[:,:,3] = Img5
    finalImage[:,:,4] = Img6
    finalImage[:,:,5] = Img7
    finalImage[:,:,6] = Img8
    finalImage[:,:,7] = Img9
    finalImage[:,:,8] = Img10

    return finalImage, bandsPresent


def rescaleALI(metaData, imgArray, availableBandsNum):

    #Rescale ALI image data
    radianceScaling = metaData['RADIANCE_SCALING']
    bandScaling = numpy.zeros(len(availableBandsNum))
    bandOffset = numpy.zeros(len(availableBandsNum))

    for i in numpy.arange(availableBandsNum.size):
        bandScaling[i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_SCALING_FACTOR'])
        bandOffset[i] = float(radianceScaling['BAND' + str(availableBandsNum[i]) + '_OFFSET'])

    #scaling and offset
    return (imgArray * 300. * bandScaling) + bandOffset


def sunCorrection(imgArray, metaData):
    sunAngle = float(metaData["PRODUCT_PARAMETERS"]["SUN_ELEVATION"])
    sunAngle = sunAngle*numpy.pi/180.
    imgArray = imgArray/numpy.sin(sunAngle)
    return imgArray

