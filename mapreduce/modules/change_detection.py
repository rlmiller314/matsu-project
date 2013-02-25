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

from osgeo import osr

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

def imageWindow(imgColSize, iBnd, windowSize):
    '''
    Given a list of tuples of the coordinates of intersection of two images, 
    this function returns a vector of the linear indices of the pixels
    in a window defined by the input windowSize, where windowSize is the border.
    The size of the rectangle containing the image is also a required input.
    '''
    
    windowAddress = []
    for bnd in iBnd:

        cw = (2*windowSize+1)*range(bnd[1]-windowSize,bnd[1]+windowSize+1)       
        rw = (2*windowSize+1)*range(bnd[0]-windowSize,bnd[0]+windowSize+1)
        rw = numpy.array(rw).reshape(2*windowSize+1,2*windowSize+1).T
        rw = list(rw.reshape(-1,))
            
        iWd = numpy.hstack(( numpy.array(rw).reshape(-1,1), numpy.array(cw).reshape(-1,1) ))
        windowAddress.append( list( iWd[:,0]*imgColSize + iWd[:,1]+1 ) )  #due to python indexing, the element with index n is the (n+1)th element

    windowAddress = numpy.array(windowAddress)
        
    return windowAddress

def changeProb(poly1, poly2, iBand1, iBand2, changeType, windowSize):
    '''
    Two types of change detection can be performed, a Bayesian(Aach et. al., Proc. IEEE Conf. on Image Processing, Vol. III 2001)
    and a spectral. Both methods take advantage of a dot product between vectors, but in different ways.
    In the Bayesian method, the gray level of each pixel in a window surrounding the pixel of interest
    is an element of a vector associated with that pixel.  A function which depends on this dot product
    forms the argument of a gaussian.  The gaussian are considered to be chi-squared distributed.
    '''
    #
    imgAddress1 = numpy.zeros((poly1.shape[0]*poly1.shape[1]),dtype=bool)
    imgAddress2 = numpy.zeros((poly2.shape[0]*poly2.shape[1]),dtype=bool)
    imgAddress1[numpy.array(iBand1)[:,0]*poly1.shape[1] + numpy.array(iBand1)[:,1] + 1] = True
    imgAddress2[numpy.array(iBand2)[:,0]*poly2.shape[1] + numpy.array(iBand2)[:,1] + 1] = True
    #

    if changeType == 1:

        imgArray1 = poly1[:,:,6:].reshape(-1,poly1.shape[2] - 6)
        imgArray2 = poly2[:,:,6:].reshape(-1,poly2.shape[2] - 6)

        T = numpy.zeros((len(iBand1)))

        imageGray1 = numpy.zeros((imgArray1.shape[0]))
        for ij in numpy.arange(imgArray1.shape[0]):
            imageGray1[ij] = numpy.sqrt(numpy.vdot(imgArray1[ij,:],imgArray1[ij,:]))

        imageGray2 = numpy.zeros((imgArray2.shape[0]))
        for ij in numpy.arange(imgArray2.shape[0]):
            imageGray2[ij] = numpy.sqrt(numpy.vdot(imgArray2[ij,:],imgArray2[ij,:]))

        Xsigma = numpy.std(imageGray1[imgAddress1])

        imageWindow1 = imageWindow(poly1.shape[1],iBand1,windowSize)
        imageWindow2 = imageWindow(poly2.shape[1],iBand2,windowSize)
        for ij in numpy.arange(len(iBand1)):
            x2 = numpy.vdot(imageGray1[imageWindow1[ij,:]],imageGray1[imageWindow1[ij,:]])
            y2 = numpy.vdot(imageGray2[imageWindow2[ij,:]],imageGray2[imageWindow2[ij,:]])
            xy = numpy.vdot(imageGray1[imageWindow1[ij,:]],imageGray2[imageWindow2[ij,:]])
            T1 = x2 * y2 - xy**2
            T2 = Xsigma**2 * (x2 + y2)
            T3 = (numpy.sqrt(2*numpy.pi)*Xsigma)**(windowSize-1)
            T[ij] = (1/T3)*numpy.exp(-(1/2)*(T1/T2))
        return T,imgArray1[imgAddress1,:],imgArray2[imgAddress2,:] 
 
    else:

        imgArray1 = poly1[:,:,6:].reshape(-1,poly1.shape[2] - 6)[imgAddress1,:]
        imgArray2 = poly2[:,:,6:].reshape(-1,poly2.shape[2] - 6)[imgAddress2,:]

        T = numpy.zeros((imgArray1.shape[0]))

        for ij in numpy.arange(imgArray1.shape[0]):
            y2 = numpy.vdot(imgArray2[ij,:],imgArray2[ij,:])
            x2 = numpy.vdot(imgArray1[ij,:],imgArray1[ij,:])
            xy = numpy.vdot(imgArray1[ij,:],imgArray2[ij,:])
            T1 = x2 * y2 - xy**2
            T2 = x2*y2
            T[ij] = T1/T2
        return T,imgArray1,imgArray2

def interpImage(poly1, poly2):
    #This sub module maps the row/column indices of polygon2 onto the row/column grid of polygon1   

    interpSize = 100j
    yy, xx = numpy.array(numpy.around(numpy.mgrid[0:(poly1[:,:,0].shape[0]-1):(3*interpSize),0:(poly1[:,:,0].shape[1]-1):interpSize]),dtype=int)

    #sample from image1
    rI1 = poly1[yy.reshape(-1,),xx.reshape(-1,),0].reshape(-1,1)   #image1 rows
    cI1 = poly1[yy.reshape(-1,),xx.reshape(-1,),1].reshape(-1,1)   #image1 columns
    yL1 = poly1[yy.reshape(-1,),xx.reshape(-1,),2].reshape(-1,1)   #image1 latitude
    xL1 = poly1[yy.reshape(-1,),xx.reshape(-1,),3].reshape(-1,1)   #image1 longitude
    aI1 = numpy.array(poly1[:,:,4].reshape(-1,),dtype=bool)
    #
    #
    yL2 = poly2[:,:,2].reshape(-1,1) #image2 latitude
    xL2 = poly2[:,:,3].reshape(-1,1) #image2 longitude
    aI2 = poly2[:,:,4].reshape(-1,)  #image2 alpha band
    oI2 = poly2[:,:,5].reshape(-1,)  #image2 polygon outline
  
    #interpolate row/columns of image2
    rI2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xL1,yL1)),rI1,numpy.hstack((xL2,yL2)),method='cubic',fill_value=-1.0)),dtype=int)
    cI2 = numpy.array(numpy.around(scipy.interpolate.griddata( numpy.hstack((xL1,yL1)),cI1,numpy.hstack((xL2,yL2)),method='cubic',fill_value=-1.0)),dtype=int)

    rI2 = rI2.reshape(-1,)
    cI2 = cI2.reshape(-1,)
    pI2 = numpy.ones((rI2.size))
    pI2[rI2<0] = 0
    pI2[cI2<0] = 0

    oR2 = rI2[numpy.array(aI2*pI2*oI2,dtype=bool)].reshape(-1,1)
    oC2 = cI2[numpy.array(aI2*pI2*oI2,dtype=bool)].reshape(-1,1)

    rI2 = rI2[numpy.array(aI2*pI2,dtype=bool)].reshape(-1,1)
    cI2 = cI2[numpy.array(aI2*pI2,dtype=bool)].reshape(-1,1)

    rI1 = poly1[:,:,0].reshape(-1,1)
    cI1 = poly1[:,:,1].reshape(-1,1)
    rI1 = rI1[aI1]
    cI1 = cI1[aI1]

    interBand = map(list,set( map(tuple,numpy.hstack((rI1,cI1)) )) & set( map(tuple,numpy.hstack((rI2,cI2)) )) )
    interBand.sort()
   
    xx=[]
    yy=[]
    yL1=[]
    xL1=[]
    rI1=[]
    cI1=[]
    aI1=[]
    yL2=[]
    xL2=[]
    rI2=[]
    cI2=[]
    aI2=[]
    oI2=[]
    pI2=[]
 
    return interBand, oR2, oC2


def newBand(geoPicture1, geoPicture2):
  with RedirectStdStreams(stdout=sys.stderr, stderr=sys.stderr):

    geoPicture = geoPicture1

    imageIndices = {}

    for zi in numpy.array([1,2]):
        if zi==2:
            geoPicture = geoPicture2

        imageArray = FloodClassUtils.radianceCorrection(geoPicture)

        #Need to create a mask of locations where all pixels are nonzero.
        alphaBand = (geoPicture.picture[:,:,geoPicture.bands.index(geoPicture.bands[0])] > 0)
        for band in geoPicture.bands[1:]:
            numpy.logical_and(alphaBand, geoPicture.picture[:,:,geoPicture.bands.index(band)], alphaBand)

        #Find size of the image array
        rasterXsize = geoPicture.picture.shape[1]
        rasterYsize = geoPicture.picture.shape[0]

        rowIndex, colIndex = numpy.mgrid[0:rasterYsize,0:rasterXsize]

        #This is an array of the alphaBand offset by 1 in all directions surrounding a pixel.
        polygons = numpy.dstack((alphaBand[1:-1,1:-1],alphaBand[:-2,1:-1],alphaBand[:-2,2:],alphaBand[1:-1,2:],alphaBand[2:,2:], \
                                                     alphaBand[2:,1:-1],alphaBand[2:,:-2],alphaBand[1:-1,:-2],alphaBand[:-2,:-2]))

        #Polygons will be an array containing "1"s on the border of the image.
        polygons = numpy.array(numpy.logical_and(polygons.sum(2) > 0,polygons.sum(2) < 9),dtype=int) #The offset array is used to detect the outline
        polygons = numpy.hstack((numpy.zeros((polygons.shape[0]+2,1)),numpy.vstack((numpy.zeros((polygons.shape[1])),polygons,numpy.zeros((polygons.shape[1])))),numpy.zeros((polygons.shape[0]+2,1))))

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

        imageIndices['image' + str(zi)] = numpy.dstack( (rowIndex, colIndex, yLat, xLong, alphaBand, polygons, imageArray) )
        imageIndices['bound' + str(zi)] = [boxLatMin,boxLatMax,boxLongMin,boxLongMax]
        imageIndices['bands' + str(zi)] = geoPicture.bands


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

    #Test whether there is any overlap, if not, don't do anything.
    crnr1 = int( (boundBox1[0] <= boundBox2[0] < boundBox1[1]) & (boundBox1[2] <= boundBox2[2] < boundBox1[3])  )
    crnr2 = int( (boundBox1[0] < boundBox2[1] <= boundBox1[1]) & (boundBox1[2] <= boundBox2[2] < boundBox1[3])  )
    crnr3 = int( (boundBox1[0] <= boundBox2[0] < boundBox1[1]) & (boundBox1[2] < boundBox2[3] <= boundBox1[3])  )
    crnr4 = int( (boundBox1[0] < boundBox2[1] <= boundBox1[1]) & (boundBox1[2] < boundBox2[3] <= boundBox1[3])  )

    chk_crnr = crnr1+crnr2+crnr3+crnr4

    if chk_crnr > 0:   #Is at least one corner from image two inside of image one

        polygon1 = imageIndices['image1']
        polygon2 = imageIndices['image2']

        presentBands1 = imageIndices['bands1']
        presentBands2 = imageIndices['bands2']

        #Only use bands common to both images for change detection
        presentBands = []
        for pB in presentBands1:
            if pB in presentBands2:
                presentBands.append([int(pB.lstrip('B')),int(presentBands1.index(pB)),int(presentBands2.index(pB))])
        presentBands = numpy.array(presentBands)
        polygon1 = numpy.dstack((polygon1[:,:,:6], polygon1[:,:,(6 + presentBands[:,1]) ] )) #Depth 6 is the beginning of the image bands. 
        polygon2 = numpy.dstack((polygon2[:,:,:6], polygon2[:,:,(6 + presentBands[:,2]) ] )) 

        imageIndices = []
        presentBands1 = []
        presentBands2 = []
        presentBands = []

        interBand1, pR2, pC2 = interpImage(polygon1,polygon2)
        interBand2, pR1, pC1 = interpImage(polygon2,polygon1)

        change_prob, imageArray1, imageArray2 = changeProb(polygon1, polygon2, interBand1,interBand2,2,1)

        #Find cloud pixels from both images to eliminate from change test
        nonCloudAddress1 = cloudFilter(imageArray1,[])
        nonCloudAddress2 = cloudFilter(imageArray2,nonCloudAddress1)

        change_prob[change_prob < 0 ] = 0
        change_prob[change_prob > 1 ] = 0
        change_prob[numpy.arange(change_prob.size)[numpy.array(1-nonCloudAddress2.reshape(-1,),dtype=bool)],:] = 0

        interBand = numpy.array(interBand1)
        #Create a rectangular array into which the parallelogram will be placed
        imageArrayFinal2 = numpy.zeros((polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],3), dtype=numpy.float)
        for ij in numpy.arange(interBand.shape[0]):
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],0] = 1 - change_prob[ij] #1
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],1] = 1 - change_prob[ij] #1-.5*change_prob[ij]
            imageArrayFinal2[interBand[ij,0],interBand[ij,1],2] = 1 - change_prob[ij] #1-.75*change_prob[ij]

        imageArrayFinal2 = imageArrayFinal2 + polygon1[:,:,5].reshape(polygon1[:,:,0].shape[0],polygon1[:,:,0].shape[1],1)

        for i in numpy.arange(pR2.shape[0]):
            imageArrayFinal2[pR2[i],pC2[i],0:3] = 1

        geoPicture.bands.extend(["CHANGE_BAND"])
        geoPicture.picture = numpy.dstack((polygon1[:,:,6:],imageArrayFinal2))


    else:
        sys.stderr.write('These two images do not overlap.')
        imageArrayFinal2 = numpy.zeros((geoPicture.picture.shape[0],geoPicture.picture.shape[1],3), dtype=numpy.float)
        geoPicture.bands.extend(["CHANGE_BAND"])
        geoPicture.picture = imageArrayFinal2


    geoPictureOutput = GeoPictureSerializer.GeoPicture()
    geoPictureOutput.picture = geoPicture.picture
    geoPictureOutput.metadata = geoPicture.metadata
    geoPictureOutput.bands = geoPicture.bands

    return geoPictureOutput


