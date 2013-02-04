#This module will compare two spatially overlapping images
#from different times, in order to create a change probability
#map.
#The necessary inputs are two geoPicture objects
#corresponding to the images to be compared.
import numpy
import scipy.interpolate
import json
import GeoPictureSerializer
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

from osgeo import osr


def newBand(geoPicture1, geoPicture2):
  with RedirectStdStreams(stdout=sys.stderr, stderr=sys.stderr):

    geoPicture = geoPicture1

    imageIndices = {}

    for zi in numpy.array([1,2]):
        if zi==2:
            geoPicture = geoPicture2 

        #load the image into an array
        imageArray = geoPicture.picture

        #create a list of bands array
        presentBands = geoPicture.bands

        #create a numerical vector corresponding to bands present
        presentBandsNum = numpy.zeros(len(presentBands))
        for i in numpy.arange(len(presentBands)):
            presentBandsNum[i] = int( presentBands[i].lstrip('B') )

        #Need to create a mask of locations where all pixels are nonzero.
        alphaBand = (geoPicture.picture[:,:,presentBands.index(presentBands[0])] > 0)
        for band in presentBands[1:]:
            numpy.logical_and(alphaBand, geoPicture.picture[:,:,presentBands.index(band)], alphaBand)

        #Find size of the image array
        rasterXsize = geoPicture.picture.shape[1]
        rasterYsize = geoPicture.picture.shape[0]

        #
        rowIndex, colIndex = numpy.mgrid[0:rasterYsize,0:rasterXsize]

        #This is an array of the alphaBand offset by 1 in all directions surrounding a pixel.
        polygons = numpy.dstack((rowIndex[1:-1,1:-1],colIndex[1:-1,1:-1],alphaBand[1:-1,1:-1],alphaBand[:-2,1:-1],alphaBand[:-2,2:],alphaBand[1:-1,2:],alphaBand[2:,2:], \
                                                     alphaBand[2:,1:-1],alphaBand[2:,:-2],alphaBand[1:-1,:-2],alphaBand[:-2,:-2]))


        polygons[:,:,2] = polygons[:,:,2:].sum(2)
        polygons = polygons[:,:,0:3]
        polygons = numpy.array(numpy.logical_and(polygons[:,:,2] > 0,polygons[:,:,2] < 9),dtype=int) #The offset array is used to detect the outline
        p1 = numpy.zeros((rasterYsize,rasterXsize))                                                  #of the image.
        p1[1:-1,1:-1] = polygons


        #There are too many points to calculate all lat/long.  Will calculate some, then interpolate.
        interpSize = 100j
        yy, xx = numpy.mgrid[0:(rasterYsize-1):(3*interpSize), 0:(rasterXsize-1):interpSize]
        yy = yy.reshape(-1,1)                                                              
        xx = xx.reshape(-1,1)
        yLat = numpy.zeros((yy.size,1))
        xLong = numpy.zeros((xx.size,1))
        for ij in numpy.arange(yy.size):
            yLat[ij], xLong[ij] = latLong(geoPicture,xx[ij,0],yy[ij,0])
        yLat = scipy.interpolate.griddata( numpy.hstack((xx,yy)), yLat, (colIndex.reshape(-1,1), rowIndex.reshape(-1,1)), method = 'cubic' )   #Use spline interpolation
        xLong = scipy.interpolate.griddata( numpy.hstack((xx,yy)), xLong, (colIndex.reshape(-1,1), rowIndex.reshape(-1,1)), method = 'cubic' ) #of calculated lat/long points
        boxLatMin, boxLongMin = latLong(geoPicture,0,rasterYsize-1)
        boxLatMax, boxLongMax = latLong(geoPicture,rasterXsize-1,0)
        yLat = yLat.reshape(rasterYsize,rasterXsize)
        xLong = xLong.reshape(rasterYsize,rasterXsize)

        imageIndices['image' + str(zi)] = numpy.dstack( (rowIndex, colIndex, yLat, xLong, alphaBand, p1, imageArray) )
        imageIndices['bound' + str(zi)] = [boxLatMin,boxLatMax,boxLongMin,boxLongMax]

        #clear some variables from memory
        imageArray = []
        presentBands = []
        presentBandsNum = []
        alphaBand = []
        rowIndex = []
        colIndex = []
        polygons = []
        p1 = []
        yy = []
        xx = []
        yLat = []
        xLong = []
                
    boundBox1 = imageIndices['bound1'] 
    boundBox2 = imageIndices['bound2']     


    crnr1 = int( (boundBox1[0] <= boundBox2[0] < boundBox1[1]) & (boundBox1[2] <= boundBox2[2] < boundBox1[3])  )
    crnr2 = int( (boundBox1[0] < boundBox2[1] <= boundBox1[1]) & (boundBox1[2] <= boundBox2[2] < boundBox1[3])  )
    crnr3 = int( (boundBox1[0] <= boundBox2[0] < boundBox1[1]) & (boundBox1[2] < boundBox2[3] <= boundBox1[3])  )
    crnr4 = int( (boundBox1[0] < boundBox2[1] <= boundBox1[1]) & (boundBox1[2] < boundBox2[3] <= boundBox1[3])  )
    chk_crnr = crnr1+crnr2+crnr3+crnr4   

    if chk_crnr > 0:
        
        polygon1 = imageIndices['image1']
        polygon2 = imageIndices['image2']
        imageIndices = [] 

        polyRC = polygon2[:,:,5].reshape(-1,)
        
        yLat2 = polygon2[:,:,2].reshape(-1,1)
        xLong2 = polygon2[:,:,3].reshape(-1,1)       

        interpSize = 100j
        yy, xx = numpy.array(numpy.around(numpy.mgrid[0:(polygon1[:,:,0].shape[0]-1):(3*interpSize),0:(polygon1[:,:,0].shape[1]-1):interpSize]),dtype=int)
        #
        yLat = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),2]
        xLong = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),3]
        #
        rowInd = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),0]
        colInd = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),1]
        #
        #
        rowInd2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xLong,yLat)),rowInd,(xLong2,yLat2),method='cubic',fill_value=-1.0)),dtype=int)
        colInd2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xLong,yLat)),colInd,(xLong2,yLat2),method='cubic',fill_value=-1.0)),dtype=int)
        rowInd2 = rowInd2.reshape(-1,)
        colInd2 = colInd2.reshape(-1,)
        posInd = numpy.ones((rowInd2.size))
        posInd[rowInd2<0] = 0
        posInd[colInd2<0] = 0
        #
        #
        alpha1 = numpy.array(polygon1[:,:,4].reshape(-1,),dtype=bool)
        alpha2 = polygon2[:,:,4].reshape(-1,)
        polyRC = polyRC*alpha2
        alpha2 = numpy.array(alpha2*posInd,dtype=bool)
        polyRC = numpy.array(polyRC,dtype=bool)
        #
        rowInd = polygon1[:,:,0].reshape(-1,1) 
        colInd = polygon1[:,:,1].reshape(-1,1)    
        rowInd = rowInd[alpha1]
        colInd = colInd[alpha1] 
        rowInd2 = rowInd2.reshape(-1,1)
        colInd2 = colInd2.reshape(-1,1)
        pR2 = rowInd2[polyRC]
        pC2 = colInd2[polyRC]
        rowInd2 = rowInd2[alpha2,:]
        colInd2 = colInd2[alpha2,:]

        #

        interBand = map(list,set( map(tuple,numpy.hstack((rowInd2,colInd2)) )) & set( map(tuple,numpy.hstack((rowInd,colInd)) )) )
        interBand.sort()

        #clear more variables
        rowInd = []
        colInd = []
        rowInd2 = []
        colInd2 = []
        yLat = []
        yLat2 = []
        xLong = []
        xLong2 = []
        alpha1 = []
        alpha2 = []
        xx = []
        yy = []
        polyRC = []
        #
        #
        imageAddress1 = numpy.zeros((polygon1.shape[0]*polygon1.shape[1]),dtype=bool)
        imageAddress2 = numpy.zeros((polygon2.shape[0]*polygon2.shape[1]),dtype=bool)
        imageAddress1[numpy.array(numpy.array(interBand)[:,0]*polygon1.shape[1]+numpy.array(interBand)[:,1],dtype=int)] = True
        imageAddress2[numpy.array(numpy.array(interBand)[:,0]*polygon2.shape[1]+numpy.array(interBand)[:,1],dtype=int)] = True
        imageArray1 = polygon1[:,:,6:].reshape(polygon1.shape[0]*polygon1.shape[1],polygon1.shape[2] - 6)[imageAddress1]
        imageArray2 = polygon2[:,:,6:].reshape(polygon2.shape[0]*polygon2.shape[1],polygon2.shape[2] - 6)[imageAddress2]


        #clear polygon2 array
        polygon2 = []
      
        #Find cloud pixels from both images to eliminate from change test
        nonCloudAddress1 = cloudFilter(imageArray1,[])
        nonCloudAddress2 = cloudFilter(imageArray2,nonCloudAddress1)

        #interBand1 = numpy.array(interBand)
        #interBand1 = interBand1[numpy.array(nonCloudAddress2.reshape(-1,),dtype=bool),:]

        Image1Sigma, Image2Sigma = pixelStats(imageArray1,imageArray2)
        change_prob = changeProb(imageArray1,imageArray2,Image1Sigma)
        change_prob = change_prob[numpy.array(nonCloudAddress2.reshape(-1,),dtype=bool)]            


        
        #Create a rectangular array into which the parallelogram will be placed
        imageArrayFinal2 = numpy.zeros((polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],3), dtype=numpy.float)
        for iB in interBand:
            imageArrayFinal2[iB[0],iB[1],0] = 1
            imageArrayFinal2[iB[0],iB[1],1] = 1-.4*change_prob[ij]
            imageArrayFinal2[iB[0],iB[1],2] = 1-.6*change_prob[ij] 
        #for ij in numpy.arange(rowInd2.shape[0]):
        #    imageArrayFinal2[rowInd2[ij,0],colInd2[ij,0],:] = 1     



        imageArrayFinal2 = imageArrayFinal2 + polygon1[:,:,5].reshape(polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],1)    

        for i in numpy.arange(pR2.shape[0]):
            imageArrayFinal2[pR2[i],pC2[i],0] = 1


        geoPicture.bands.extend(["CHANGE_BAND"])
        geoPicture.picture = numpy.dstack((polygon1[:,:,6:],imageArrayFinal2))

        #clear variables
        
        nonCloudAddress1 = []
        nonCloudAddress2 = []
        Image1Sigma = []
        Image2Sigma = []
        interBand = []
        imageArrayFinal2 = []





    else:
        sys.stderr.write('These two images do not overlap.')
        imageArrayFinal2 = numpy.zeros((polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],3), dtype=numpy.float)
        geoPicture.bands.extend(["CHANGE_BAND"])
        geoPicture.picture = imageArrayFinal2 



    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.picture = geoPicture.picture
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = geoPicture.bands

    return geoPictureOutput


def cloudFilter(imgArray,nCA):
    if nCA == []:
        nCA = numpy.ones(imgArray.shape[0])
    T1 = numpy.mean( (imgArray*imgArray).sum(1) ) + numpy.std( (imgArray*imgArray).sum(1) )
    nCA[ (imgArray*imgArray).sum(1) > T1 ] = 0
    return nCA


def latLong(geoPic, x, y):
    # Convert an (x, y) pixel position into a (longitdue, latitude) pair.
    # Note that the array is indexed as array[y, x] and coordinates passed to this function need not be integers.
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(geoPic.metadata["Projection"])
    coordinateTransform = osr.CoordinateTransformation(spatialReference, spatialReference.CloneGeogCS())
    tlx, weres, werot, tly, nsrot, nsres = json.loads(geoPic.metadata["GeoTransform"])
    longitude, latitude, altitude = coordinateTransform.TransformPoint(tlx + weres * x, tly + nsres * y)
    return latitude, longitude


def pixelStats(imageOne, imageTwo):
    Xsigma = numpy.std(imageOne,1)
    Xsigma = Xsigma.reshape(-1,1)

    Ysigma = numpy.std(imageTwo,1)
    Ysigma = Ysigma.reshape(-1,1)

    return Xsigma, Ysigma

def changeProb(Ypixel, Xpixel, Xsigma):
    T = numpy.zeros((Ypixel.shape[0]))
    for ij in numpy.arange(Ypixel.shape[0]):
        T1 = numpy.vdot(Ypixel[ij,:],Ypixel[ij,:]) * numpy.vdot(Xpixel[ij,:],Xpixel[ij,:]) - numpy.vdot(Xpixel[ij,:],Ypixel[ij,:])**2
        T2 = Xsigma[ij]**2 * (numpy.vdot(Xpixel[ij,:],Xpixel[ij,:]) + numpy.vdot(Ypixel[ij,:],Ypixel[ij,:]))
        T[ij] = ((1/(numpy.sqrt(2*numpy.pi)*T2))**(Xpixel.shape[1]-1))*numpy.exp(-(1/2)*(T1/T2))    
    return T


