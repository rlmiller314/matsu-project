#trainingSet.py
#this python module is used to construct
#training data sets

import numpy
import time
import os
import sys

import GeoPictureSerializer
import FloodClassUtils

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

def main(trainingDirectory, landCoverList, band_list=[], band_weight_list=[]):

    
    #If bandList is empty, i.e., no band grouping list was input at command line. A default list, contained in FloodClassUtils.py,
    # will be used.
    #Note that if a "band_weight_list" is input, it should correspond with the band_list, and it should be known apriori that 
    #all serialized files input to this code contain the required bands.

    if band_list==[]:
        band_list = FloodClassUtils.bandList()
 
    landCoverTypesListLength = 10**50
    landCoverTypes = {}

    flagTwo = True

    for landName in landCoverList:

        flagOne = True

        fileList = os.listdir(trainingDirectory + "/" + landName)
        for serialFile in fileList:

            #read in and deserialize
            geoPicture = GeoPictureSerializer.deserialize(open(trainingDirectory + "/" + landName + "/" +serialFile))

            #do radiance correction on bands
            geoPicture = FloodClassUtils.radianceCorrection(geoPicture) 
             
            #find bands common to training set and requested set
            finalBandList, bandsPresent = FloodClassUtils.commonBand(geoPicture,band_list)

            #Combine bands
            geoPicture.picture = FloodClassUtils.bandSynth(geoPicture,finalBandList,band_weight_list)

            #The band list of common bands are added to the geoPicture to replace the original
            geoPicture.bands = bandsPresent


            missingBandList=[]
            for i in numpy.arange(len(FloodClassUtils.bandList())):
                missingBandSet = set(FloodClassUtils.bandList()[i]) - set(finalBandList[i])
                missingBandList.append(list(missingBandSet))             
            sys.stderr.write("\nThe following requested bands are missing from serialized file "+str(serialFile)+":\n"+str(missingBandList)+"\n")

            #Need to create a mask of locations where all pixels are nonzero.
            alphaBand = (geoPicture.picture[:,:,geoPicture.bands.index(geoPicture.bands[0])] > 0)
            for band in geoPicture.bands[1:]:
                numpy.logical_and(alphaBand, geoPicture.picture[:,:,geoPicture.bands.index(band)], alphaBand)

            #Make bands into 2-d array
            #Find size of the image array
            rasterXsize = geoPicture.picture.shape[1]
            rasterYsize = geoPicture.picture.shape[0]
            rasterDepth = geoPicture.picture.shape[2]

            #Reshape all arrays
            geoPicture.picture = geoPicture.picture.reshape(rasterXsize*rasterYsize,rasterDepth)
            alphaBand = alphaBand.reshape(rasterXsize*rasterYsize)
            geoPicture.picture = geoPicture.picture[alphaBand,:]


            if flagOne==True:
                landCoverTypes[landName] = geoPicture.picture
                flagOne = False
            else:
                landCoverTypes[landName] = numpy.concatenate( (landCoverTypes[landName],geoPicture.picture),axis=0 )
  
        #Note that the classification digit is tied to the order of the landCoverList, i.e., classification digit = landCoverList_position + 1
        landCoverTypes[landName] = numpy.concatenate( (landCoverTypes[landName],(landCoverList.index(landName)+1)*numpy.ones((landCoverTypes[landName].shape[0],1),dtype=int)), axis=1 )
        landCoverTypes[landName] = landCoverTypes[landName][ numpy.random.permutation( landCoverTypes[landName].shape[0] ), :]
        landCoverTypesListLength = min(landCoverTypes[landName].shape[0],landCoverTypesListLength)
 
        if flagTwo==True:
            sampleLength = numpy.minimum(5000,landCoverTypesListLength)
            train = landCoverTypes[landName][:sampleLength,:]
            flagTwo = False
        else:
            train = numpy.concatenate( (train,landCoverTypes[landName][:sampleLength,:]), axis=0 )

    numpy.savetxt('trainingSet.txt',train,fmt=rasterDepth*'%-12.5f '+'%-d')

