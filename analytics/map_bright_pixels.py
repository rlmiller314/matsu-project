#!/usr/bin/env python

import sys
import json

from osgeo import osr

import GeoPictureSerializer

def map_bright_pixels(inputStream, outputStream, band, modules=None):
    loadedModules = []
    if modules is not None:
        for module in modules:
            globalVars = {}
            exec(compile(open(module).read(), module, "exec"), globalVars)
            loadedModules.append(globalVars["newBand"])

    while True:
        line = inputStream.readline()
        if not line: break

        try:
            geoPicture = GeoPictureSerializer.deserialize(line)
        except IOError:
            continue

        for newBand in loadedModules:
            geoPicture = newBand(geoPicture)

        picture = geoPicture.picture[:,:,geoPicture.bands.index(band)]






if __name__ == "__main__":
    osr.UseExceptions()

    band = sys.argv[1]
    modules = sys.argv[2:]

    map_bright_pixels(sys.stdin, sys.stdout, band, modules=modules)
