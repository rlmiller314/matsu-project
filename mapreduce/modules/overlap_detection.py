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
        presentBandsNum = numpy.zeros(len(presentBands), dtype=numpy.uint8)
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
        interpSize = 500j
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

        #
        
        p2xy = [0,rasterYsize-1,0,rasterXsize-1]
        y2Min = numpy.maximum(boundBox1[1] - polygon2[:,:,2][:,0],0)
        y2Min = y2Min[y2Min>0] 
        y2Max = numpy.maximum(polygon2[:,:,2][:,0] - boundBox1[0],0)
        y2Max = y2Max[y2Max>0] 
        x2Min = numpy.maximum(polygon2[:,:,3][0,:] - boundBox1[2],0)
        x2Min = x2Min[x2Min>0] 
        x2Max = numpy.maximum(boundBox1[3] - polygon2[:,:,3][0,:],0)
        x2Max = x2Max[x2Max>0] 

        if y2Min != []:
            y2Min = numpy.amin(y2Min)
            y2MinIndex = list(boundBox1[1] - polygon2[:,:,2][:,0]).index(y2Min)
            p2xy[0] = y2MinIndex  
        if y2Max != []:        
            y2Max = numpy.amin(y2Max)
            y2MaxIndex = list(polygon2[:,:,2][:,0] - boundBox1[0]).index(y2Max)
            p2xy[1] = y2MaxIndex 
        if x2Min != []:
            x2Min = numpy.amin(x2Min)
            x2MinIndex = list(polygon2[:,:,3][0,:] - boundBox1[2]).index(x2Min)
            p2xy[2] = x2MinIndex 
        if x2Max != []:
            x2Max = numpy.amin(x2Max)
            x2MaxIndex = list(boundBox1[3] - polygon2[:,:,3][0,:]).index(x2Max)
            p2xy[3] = x2MaxIndex 

        yLat2 = polygon2[p2xy[0]:p2xy[1]+1,p2xy[2]:p2xy[3]+1,2].reshape(-1,1)
        xLong2 = polygon2[p2xy[0]:p2xy[1]+1,p2xy[2]:p2xy[3]+1,3].reshape(-1,1)
         
        polyRC = numpy.array(polygon2[p2xy[0]:p2xy[1],p2xy[2]:p2xy[3],5],dtype=bool).reshape(-1,)
        

        interpSize = 500j
        yy, xx = numpy.uint(numpy.around(numpy.mgrid[0:(polygon1[:,:,0].shape[0]-1):(3*interpSize),0:(polygon1[:,:,0].shape[1]-1):interpSize]))
        #
        yLat = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),2]
        xLong = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),3]
        #
        rowInd = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),0]
        colInd = polygon1[yy.reshape(-1,1),xx.reshape(-1,1),1]
        xx = []
        yy = []
        #
        #
        rowInd2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xLong,yLat)),rowInd,(xLong2,yLat2),method='cubic')),dtype=int)
        colInd2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xLong,yLat)),colInd,(xLong2,yLat2),method='cubic')),dtype=int)
        rowInd2 = rowInd2.reshape(-1,1)
        colInd2 = colInd2.reshape(-1,1)
        #
        #pR2 = rowInd2[polyRC]
        #pC2 = colInd2[polyRC]
        #pR2 = pR2[pR2 > 0]
        

        alpha1 = numpy.array(polygon1[:,:,4].reshape(-1,),dtype=bool)
        alpha2 = numpy.array(polygon2[p2xy[0]:p2xy[1],p2xy[2]:p2xy[3],4].reshape(-1,),dtype=bool)
        
        rowInd = polygon1[:,:,0].reshape(-1,1) 
        colInd = polygon1[:,:,1].reshape(-1,1)    
        rowInd = rowInd[alpha1]
        colInd = colInd[alpha1] 
        rowInd2 = rowInd2[alpha2]
        colInd2 = colInd2[alpha2]
        #pR2 = rowInd2[polyRC]
        #pC2 = colInd2[polyRC]
        interBand = map(list,set( map(tuple,numpy.hstack((rowInd2,colInd2)) )) & set( map(tuple,numpy.hstack((rowInd,colInd)) )) )
        interBand.sort()
        rowInd = []
        colInd = []
        rowInd2 = []
        colInd2 = []
        alpha1 = []
        alpha2 = []
        #
        #
        interBand = numpy.array(interBand)
        imageArray1 = numpy.zeros((1,polygon1[:,:,6:].shape[2]))
        imageArray2 = numpy.zeros((1,polygon2[:,:,6:].shape[2]))
        for ij in numpy.arange(interBand.shape[0]):
            imageArray1 = numpy.append(imageArray1,numpy.array([polygon1[interBand[ij,0],interBand[ij,1],6:]]),axis=0)
            imageArray2 = numpy.append(imageArray2,numpy.array([polygon2[interBand[ij,0],interBand[ij,1],6:]]),axis=0)  
        imageArray1 = imageArray1[1:,:]
        imageArray2 = imageArray2[1:,:]
        p1Shape0 = polygon1[:,:,0].shape[0]
        p2Shape1 = polygon2[:,:,0].shape[1]
        #polygon1 = []
        polygon2 = []
      

        #Find cloud pixels from both images to eliminate from change test
        nonCloudAddress1 = cloudFilter(imageArray1,[])
        nonCloudAddress2 = cloudFilter(imageArray2,nonCloudAddress1)

        interBand = interBand[numpy.array(nonCloudAddress2.reshape(-1,1),dtype=bool)]

        Image1Sigma, Image2Sigma = pixelStats(imageArray1,imageArray2)
        change_prob = changeProb(imageArray1,imageArray2,Image1Sigma)
        change_prob = change_prob[numpy.array(nonCloudAddress2.reshape(-1,1),dtype=bool)]            
 
        #Create a rectangular array into which the parallelogram will be placed
        imageArrayFinal2 = numpy.zeros((p1Shape0,p1Shape1,3), dtype=numpy.float)
        for ij in numpy.arange(interBand.shape[0]):
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],0] = 1 - change_prob[ij]
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],1] = 1 - change_prob[ij]
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],0] = 1 

        imageArrayFinal2 = imageArrayFinal2 + polygon1[:,:,5].reshape(polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],1)    

        #for i in numpy.arange(pR2.shape[0]):
        #    imageArrayFinal2[pR2[i],pC2[i],0] = 1


        #imageArray1 = iamgeArray.reshape(-1,polygon1.shape[2])
        #imageArray1 = imageArray[numpy.array(nonCloudAddress2.reshape(-1,1),dtype=bool)]
 
        #imageArray2 = polygon2[:,:,6:].reshape(polygon2.shape[0]*polygon2.shape[1],polygon2.shape[2])
        #imageArray2 = imageArray2[numpy.array(nonCloudAddress2.reshape(-1,1),dtype=bool)]


        geoPicture.bands.extend(["CHANGE_BAND"])
        geoPicture.picture = imageArrayFinal2


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
    #T1 = ((Ypixel*Ypixel).sum(1))**2 * ((Xpixel*Xpixel).sum(1))**2 - ((Xpixel*Ypixel).sum(1))**2
    #T2 = Xsigma**2 * ((Xpixel*Xpixel).sum(1))**2 + ((Ypixel*Ypixel).sum(1))**2
    T1 = numpy.square(numpy.dot(Ypixel,Ypixel.T).diagonal()) * numpy.square(numpy.dot(Xpixel,Xpixel.T).diagonal()) - numpy.square(numpy.dot(Xpixel,Ypixel.T).diagonal())
    T2 = numpy.square(Xsigma) * numpy.square(numpy.dot(Xpixel,Xpixel.T).diagonal()) + numpy.square(numpy.dot(YPixel,YPixel.T).diagonal())
    T = T1/T2
    return T


