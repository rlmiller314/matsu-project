#!/usr/bin/env python

import sys
import json
import datetime
import time

import numpy
from osgeo import osr

import GeoPictureSerializer

def map_bright_pixels(inputStream, outputStream, band, threshold, modules=None):
    loadedModules = []
    if modules is not None:
        for module in modules:
            globalVars = {}
            exec(compile(open(module).read(), module, "exec"), globalVars)
            loadedModules.append(globalVars["newBand"])

    while True:
        # load a picture
        line = inputStream.readline()
        if not line: break

        try:
            geoPicture = GeoPictureSerializer.deserialize(line)
        except IOError:
            continue

        # generate new bands
        for newBand in loadedModules:
            geoPicture = newBand(geoPicture)

        # prepare a transform function for this picture
        tlx, weres, werot, tly, nsrot, nsres = json.loads(geoPicture.metadata["GeoTransform"])
        spatialReference = osr.SpatialReference()
        spatialReference.ImportFromWkt(geoPicture.metadata["Projection"])
        coordinateTransform = osr.CoordinateTransformation(spatialReference, spatialReference.CloneGeogCS())

        # get the relevant band
        picture = geoPicture.picture[:,:,geoPicture.bands.index(band)]

        if isinstance(threshold, basestring) and threshold[-1] == "%":
            threshold = numpy.percentile(picture, float(threshold[:-1]))
            
        # loop over indicies that are above threshold
        for i, j in numpy.argwhere(picture > threshold):
            longitude, latitude, altitude = coordinateTransform.TransformPoint(tlx + j*weres, tly + i*nsres)

            timestamp = time.mktime(datetime.datetime.strptime(json.loads(geoPicture.metadata["L1T"])["PRODUCT_METADATA"]["START_TIME"], "%Y %j %H:%M:%S").timetuple())

            # ultimately, longitude/latitude points should map to different keys, one key per reducer
            # for now, there is only one key: world
            sys.stdout.write("world\t%g %g %d %g\n" % (longitude, latitude, timestamp, picture[i,j]))

if __name__ == "__main__":
    osr.UseExceptions()

    band = sys.argv[1]
    threshold = sys.argv[2]
    modules = sys.argv[3:]

    map_bright_pixels(sys.stdin, sys.stdout, band, threshold, modules=modules)
