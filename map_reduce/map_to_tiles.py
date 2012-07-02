import sys
import json
from math import floor, ceil

import numpy
from scipy.ndimage.interpolation import affine_transform
from osgeo import osr

import GeoPictureSerializer

osr.UseExceptions()

def tileIndex(depth, longitude, latitude):
    "Inputs a depth and floating-point longitude and latitude, outputs a triple of index integers."
    if abs(latitude) > 90.: raise ValueError("Latitude cannot be %s" % str(latitude))
    longitude += 180.
    latitude += 90.
    while longitude <= 0.: longitude += 360.
    while longitude > 360.: longitude -= 360.
    longitude = int(floor(longitude/360. * 2**depth))
    latitude = min(int(floor(latitude/180. * 2**depth)), 2**depth - 1)
    return depth, longitude, latitude

def tileName(depth, longitude, latitude):
    "Inputs an index-triple, outputs a string-valued name for the index."
    return "T%02d-%05d-%05d" % (depth, longitude, latitude)  # constant length up to depth 16

def tileCorners(depth, longitude, latitude):
    "Inputs an index-triple, outputs the floating-point corners of the tile."
    longmin = longitude*360./2**depth - 180.
    longmax = (longitude + 1)*360./2**depth - 180.
    latmin = latitude*180./2**depth - 90.
    latmax = (latitude + 1)*180./2**depth - 90.
    return longmin, longmax, latmin, latmax

def map_to_tiles(inputStream, depth, longpixels, latpixels, numLatitudeSections):
    # get the Level-1 image
    geoPicture = GeoPictureSerializer.deserialize(inputStream)

    # convert GeoTIFF coordinates into degrees
    tlx, weres, werot, tly, nsrot, nsres = json.loads(geoPicture.metadata["GeoTransform"])
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(geoPicture.metadata["Projection"])
    coordinateTransform = osr.CoordinateTransformation(spatialReference, spatialReference.CloneGeogCS())
    rasterXSize = geoPicture.picture.shape[1]
    rasterYSize = geoPicture.picture.shape[0]
    rasterDepth = geoPicture.picture.shape[2]

    for section in xrange(numLatitudeSections):
        bottom = (section + 0.0)/numLatitudeSections
        middle = (section + 0.5)/numLatitudeSections
        thetop = (section + 1.0)/numLatitudeSections

        # find the corners to determine which tile(s) this section belongs in
        corner1Long, corner1Lat, altitude = coordinateTransform.TransformPoint(tlx + 0.0*weres*rasterXSize, tly + bottom*nsres*rasterYSize)
        corner2Long, corner2Lat, altitude = coordinateTransform.TransformPoint(tlx + 0.0*weres*rasterXSize, tly + thetop*nsres*rasterYSize)
        corner3Long, corner3Lat, altitude = coordinateTransform.TransformPoint(tlx + 1.0*weres*rasterXSize, tly + bottom*nsres*rasterYSize)
        corner4Long, corner4Lat, altitude = coordinateTransform.TransformPoint(tlx + 1.0*weres*rasterXSize, tly + thetop*nsres*rasterYSize)

        outputPictures = {}
        for tileIndex in tileIndex(depth, corner1Long, corner1Lat), tileIndex(depth, corner2Long, corner2Lat), tileIndex(depth, corner3Long, corner3Lat), tileIndex(depth, corner4Long, corner4Lat):
            if tileIndex not in outputPictures:
                outputPictures[tileIndex] = numpy.zeros((latpixels, longpixels, rasterDepth), dtype=geoPicture.picture.dtype)

        for tileIndex, outputPicture in outputPictures.items():
            longmin, longmax, latmin, latmax = tileCorners(*tileIndex)

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

            # correct for the curvature of the Earth between the top of the section and the bottom of the section (that's why we cut into latitude sections)
            curvature_correction = L1TIFF_to_geo_trans * (geo_to_L1TIFF_trans * numpy.matrix([[leftLat - cornerLat], [leftLong - cornerLong]], dtype=numpy.double) - numpy.matrix([[(middle*rasterYSize)], [0.]], dtype=numpy.double))

            offset = L1TIFF_to_geo_trans.I * (offset_in_deg - truncate_correction - curvature_correction)

            # lay the GeoTIFF into the output image array
            offset = offset[0,0], offset[1,0]
            affine_transform(geoPicture.picture[int(floor(bottom*rasterYSize)):int(ceil(thetop*rasterYSize)),:,:], trans, offset, (latpixels, longpixels, rasterDepth), outputPicture)
            outputGeoPicture = GeoPictureSerializer.GeoPicture()
            outputGeoPicture.picture = outputPicture
            outputGeoPicture.metadata = geoPicture.metadata
            outputGeoPicture.bands = geoPicture.bands

            sys.stdout.write(tileName(*tileIndex) + "\t")
            outputGeoPicture.serialize(sys.stdout)
            sys.stdout.write("\n")
