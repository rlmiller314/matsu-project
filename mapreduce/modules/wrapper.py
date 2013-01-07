import numpy
import types

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

rpy2.robjects.numpy2ri.activate()

from PIL import Image

import GeoPictureSerializer
import trainingSet

def main(inputFile, classificationType=1, dataType=1, programType=1,Train=False):
    #inputFile is full path + file name as a string
    #classificationType is 1=support vector machine, 2 = naive Bayes, 3 = trees
    #dataType is 1 = magnitudes of band reflectivity, 2 = ratios of band reflectivity
    #programType is 1 = R, 2 = Python


    #The first input of trainingSet.main is a string containing the full path to training image data
    #The second input of trainingSet.main is a list of names corresponding to land cover types, which 
    #need to be the names of sub-directories in the training image data directory.
    if Train:
        trainingSet.main('/Users/ryanmiller/amazon/mnt2/training_serialized',['cloud','land_dry','water','land_veg'])

    geoPicture = GeoPictureSerializer.deserialize(open(inputFile))

    if programType==1: 
        #install the required R package
        if classificationType==3:
            robjects.r('install.packages("rpart",repos="http://rweb.quant.ku.edu/cran/")')
        else:
            robjects.r('install.packages("e1071",repos="http://rweb.quant.ku.edu/cran/")')
        #load module
        modules=['flood_detection_ThreeBand_R.py']
    else:
        #load module
        modules=['flood_detection_ThreeBand_PY.py']

    #construct the newBand module
    loadedModules = []
    if modules is not None:
        for module in modules:
            globalVars = {}
            exec(compile(open(module).read(), module, "exec"), globalVars)
            loadedModules.append(globalVars["newBand"])
    
    for newBand in loadedModules:
        geoPicture = newBand(geoPicture,classificationType,dataType)


    #image processing#
    #class image
    imageArrayClass = numpy.array(geoPicture.picture[:,:,-3:]*255, dtype=numpy.uint8)  #Compress to 3 bands for RGB image
    imageClass = Image.fromarray(imageArrayClass)
    imageClass.save( "tmpClass" + ".png", "PNG", option="optimize")

    return geoPicture
