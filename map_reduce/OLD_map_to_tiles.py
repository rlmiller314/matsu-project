import os
from math import floor, ceil

import numpy
from scipy.ndimage.interpolation import affine_transform
from PIL import Image
from osgeo import gdal
from osgeo import osr
from osgeo import gdalconst

gdal.UseExceptions()
osr.UseExceptions()

# TODO: in the future, this should seek out L1TIFFs that fit within the box and fill the PNGs in a loop (extend the existing loop)

def level1to2(inputRed, inputGreen, inputBlue, outputStream, longmin, longmax, latmin, latmax, longpixels=512, latpixels=256, numberOfSections=1):
    # get three Level-1 images
    geotiff_red = gdal.Open(inputRed, gdalconst.GA_ReadOnly)
    geotiff_green = gdal.Open(inputGreen, gdalconst.GA_ReadOnly)
    geotiff_blue = gdal.Open(inputBlue, gdalconst.GA_ReadOnly)

    # convert GeoTIFF coordinates into degrees
    tlx, weres, werot, tly, nsrot, nsres = geotiff_red.GetGeoTransform()
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(geotiff_red.GetProjection())
    coordinateTransform = osr.CoordinateTransformation(spatialReference, spatialReference.CloneGeogCS())
    rasterXSize = geotiff_red.RasterXSize
    rasterYSize = geotiff_red.RasterYSize

    # the output image array
    output_red = numpy.zeros((latpixels, longpixels), dtype=numpy.int16)
    output_green = numpy.zeros((latpixels, longpixels), dtype=numpy.int16)
    output_blue = numpy.zeros((latpixels, longpixels), dtype=numpy.int16)
    output_alpha = numpy.zeros((latpixels, longpixels), dtype=numpy.uint8)

    # convert GeoTIFF images to NumPy
    array_red = geotiff_red.ReadAsArray()
    array_green = geotiff_green.ReadAsArray()
    array_blue = geotiff_blue.ReadAsArray()

    # find the empty regions of the image (where all channels equal zero)
    array_alpha = array_red > 0
    numpy.logical_or(array_alpha, array_green > 0, array_alpha)
    numpy.logical_or(array_alpha, array_blue > 0, array_alpha)
    array_alpha.dtype = numpy.uint8
    numpy.multiply(array_alpha, 255, array_alpha)

    # lay the GeoTIFF into the output image array in slices of limited latitude
    for section in xrange(numberOfSections):
        bottom = (section + 0.0)/numberOfSections
        middle = (section + 0.5)/numberOfSections
        thetop = (section + 1.0)/numberOfSections

        # find the origin and orientation of the image (not always exactly north-south-east-west)
        cornerLong, cornerLat, altitude   = coordinateTransform.TransformPoint(tlx, tly)
        originLong, originLat, altitude   = coordinateTransform.TransformPoint(tlx + 0.5*weres*rasterXSize, tly + middle*nsres*rasterYSize)
        leftLong, leftLat, altitude       = coordinateTransform.TransformPoint(tlx + 0.0*weres*rasterXSize, tly + middle*nsres*rasterYSize)
        rightLong, rightLat, altitude     = coordinateTransform.TransformPoint(tlx + 1.0*weres*rasterXSize, tly + middle*nsres*rasterYSize)
        upLong, upLat, altitude           = coordinateTransform.TransformPoint(tlx + 0.5*weres*rasterXSize, tly + bottom*nsres*rasterYSize)
        downLong, downLat, altitude       = coordinateTransform.TransformPoint(tlx + 0.5*weres*rasterXSize, tly + thetop*nsres*rasterYSize)

        # do some linear algebra to convert coordinates
        L2PNG_to_geo_trans = numpy.matrix([[(latmin - latmax)/float(latpixels), 0.], [0., (longmax - longmin)/float(longpixels)]])

        L1TIFF_to_geo_trans = numpy.matrix([[(downLat - upLat)/((thetop - bottom)*rasterYSize), (rightLat - leftLat)/rasterXSize], [(downLong - upLong)/((thetop - bottom)*rasterYSize), (rightLong - leftLong)/rasterXSize]])
        geo_to_L1TIFF_trans = L1TIFF_to_geo_trans.I

        trans = geo_to_L1TIFF_trans * L2PNG_to_geo_trans

        offset_in_deg = numpy.matrix([[latmax - cornerLat], [longmin - cornerLong]], dtype=numpy.double)

        # correct for the bottom != 0. case (only if section > 0)
        truncate_correction = L1TIFF_to_geo_trans * numpy.matrix([[int(floor(bottom*rasterYSize))], [0.]], dtype=numpy.double)

        # correct for the curvature of the Earth between the top of the image and the bottom of the image
        curvature_correction = L1TIFF_to_geo_trans * (geo_to_L1TIFF_trans * numpy.matrix([[leftLat - cornerLat], [leftLong - cornerLong]], dtype=numpy.double) - numpy.matrix([[(middle*rasterYSize)], [0.]], dtype=numpy.double))

        offset = L1TIFF_to_geo_trans.I * (offset_in_deg - truncate_correction - curvature_correction)

        # lay the GeoTIFF into the output image array and combine into the output
        offset = offset[0,0], offset[1,0]

        # do the affine transformation in-place if you can
        if section == 0:
            affine_transform(array_red[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels), output_red)
            affine_transform(array_green[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels), output_green)
            affine_transform(array_blue[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels), output_blue)
            affine_transform(array_alpha[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels), output_alpha)

        else:
            transformed_red = affine_transform(array_red[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels))
            numpy.maximum(output_red, transformed_red, output_red)

            transformed_green = affine_transform(array_green[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels))
            numpy.maximum(output_green, transformed_green, output_green)

            transformed_blue = affine_transform(array_blue[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels))
            numpy.maximum(output_blue, transformed_blue, output_blue)

            transformed_alpha = affine_transform(array_alpha[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:], trans, offset, (latpixels, longpixels))
            numpy.maximum(output_alpha, transformed_alpha, output_alpha)

    # find the maximum value (to maximize contrast for this example)
    maxvalue = max(output_red.max(), output_green.max(), output_blue.max())

    # manipulate the array with in-place operations
    for output in "output_red", "output_green", "output_blue":
        tmp = eval(output)
        numpy.multiply(tmp, 256./maxvalue, tmp)
        tmp.dtype = numpy.uint8
        tmp = tmp[:,::2]
        exec("%s = tmp" % output)

    colorarray = numpy.dstack((output_red, output_green, output_blue, output_alpha))

    # use PIL to write the PNG file
    image = Image.fromarray(colorarray)
    image.save(outputStream, "PNG", option="optimize")

    # write out the 16-bit arrays somewhere else? (for statistical processing)
