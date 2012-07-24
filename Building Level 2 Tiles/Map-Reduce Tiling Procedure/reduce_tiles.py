import sys
import subprocess
import StringIO
import base64
import json

import numpy
from PIL import Image
from scipy.ndimage.interpolation import affine_transform

import GeoPictureSerializer

from tile_definition import *

def reduce_tiles(tiles, inputStream, outputDirectory=None, outputAccumulo=None, bands=["B029", "B023", "B016"], layer="RGB", minRadiance=0., maxRadiance=300.):
    while True:
        line = inputStream.readline()
        if not line: break

        tabPosition = line.index("\t")
        key = line[:tabPosition]
        value = line[tabPosition+1:-1]

        depth, longIndex, latIndex, timestamp = map(int, key.lstrip("T").split("-"))

        geoPicture = GeoPictureSerializer.deserialize(value)

        if (depth, longIndex, latIndex) not in tiles:
            shape = geoPicture.picture.shape[:2]
            outputRed = numpy.zeros(shape, dtype=numpy.uint8)
            outputGreen = numpy.zeros(shape, dtype=numpy.uint8)
            outputBlue = numpy.zeros(shape, dtype=numpy.uint8)
            outputMask = numpy.zeros(shape, dtype=numpy.uint8)
            tiles[depth, longIndex, latIndex] = (outputRed, outputGreen, outputBlue, outputMask)
        outputRed, outputGreen, outputBlue, outputMask = tiles[depth, longIndex, latIndex]

        red = geoPicture.picture[:,:,geoPicture.bands.index(bands[0])]
        green = geoPicture.picture[:,:,geoPicture.bands.index(bands[1])]
        blue = geoPicture.picture[:,:,geoPicture.bands.index(bands[2])]

        # TODO: divide by expected radiance based on sun's angle so that all images are equally normalized, independent of the acquisition time

        red = numpy.minimum(numpy.maximum((red - minRadiance) / (maxRadiance - minRadiance) * 255, 0), 255)
        green = numpy.minimum(numpy.maximum((green - minRadiance) / (maxRadiance - minRadiance) * 255, 0), 255)
        blue = numpy.minimum(numpy.maximum((blue - minRadiance) / (maxRadiance - minRadiance) * 255, 0), 255)
        mask = numpy.minimum(numpy.maximum(geoPicture.picture[:,:,geoPicture.bands.index("MASK")] * 255, 0), 255)

        condition = (mask > 0.5)
        outputRed[condition] = red[condition]
        outputGreen[condition] = green[condition]
        outputBlue[condition] = blue[condition]
        outputMask[condition] = mask[condition]

        image = Image.fromarray(numpy.dstack((outputRed, outputGreen, outputBlue, outputMask)))
        if outputDirectory is not None:
            image.save("%s/%s.png" % (outputDirectory, tileName(depth, longIndex, latIndex)), "PNG", options="optimize")
        if outputAccumulo is not None:
            buff = StringIO.StringIO()
            image.save(buff, "PNG", options="optimize")
            outputAccumulo.stdin.write(json.dumps({"KEY": "%s_%s" % (tileName(depth, longIndex, latIndex), layer), "L2PNG": base64.b64encode(buff.getvalue())}))
            outputAccumulo.stdin.write("\n")

def collate(depth, tiles, outputDirectory=None, outputAccumulo=None, layer="RGB", splineOrder=3):
    for depthIndex, longIndex, latIndex in tiles.keys():
        if depthIndex == depth:
            parentDepth, parentLongIndex, parentLatIndex = tileParent(depthIndex, longIndex, latIndex)
            if (parentDepth, parentLongIndex, parentLatIndex) not in tiles:
                shape = tiles[depthIndex, longIndex, latIndex][0].shape
                outputRed = numpy.zeros(shape, dtype=numpy.uint8)
                outputGreen = numpy.zeros(shape, dtype=numpy.uint8)
                outputBlue = numpy.zeros(shape, dtype=numpy.uint8)
                outputMask = numpy.zeros(shape, dtype=numpy.uint8)
                tiles[parentDepth, parentLongIndex, parentLatIndex] = outputRed, outputGreen, outputBlue, outputMask
            outputRed, outputGreen, outputBlue, outputMask = tiles[parentDepth, parentLongIndex, parentLatIndex]
            rasterYSize, rasterXSize = outputRed.shape

            inputRed, inputGreen, inputBlue, inputMask = tiles[depthIndex, longIndex, latIndex]
            
            trans = numpy.matrix([[2., 0.], [0., 2.]])
            offset = 0., 0.

            affine_transform(inputRed, trans, offset, (rasterYSize, rasterXSize), inputRed, splineOrder)
            affine_transform(inputGreen, trans, offset, (rasterYSize, rasterXSize), inputGreen, splineOrder)
            affine_transform(inputBlue, trans, offset, (rasterYSize, rasterXSize), inputBlue, splineOrder)
            affine_transform(inputMask, trans, offset, (rasterYSize, rasterXSize), inputMask, splineOrder)

            longOffset, latOffset = tileOffset(depthIndex, longIndex, latIndex)
            if longOffset == 0:
                longSlice = slice(0, rasterXSize/2)
            else:
                longSlice = slice(rasterXSize/2, rasterXSize)
            if latOffset == 0:
                latSlice = slice(rasterYSize/2, rasterYSize)
            else:
                latSlice = slice(0, rasterYSize/2)

            outputRed[latSlice,longSlice] = inputRed[0:rasterYSize/2,0:rasterXSize/2]
            outputGreen[latSlice,longSlice] = inputGreen[0:rasterYSize/2,0:rasterXSize/2]
            outputBlue[latSlice,longSlice] = inputBlue[0:rasterYSize/2,0:rasterXSize/2]
            outputMask[latSlice,longSlice] = inputMask[0:rasterYSize/2,0:rasterXSize/2]

            image = Image.fromarray(numpy.dstack((outputRed, outputGreen, outputBlue)))
            if outputDirectory is not None:
                image.save("%s/%s.png" % (outputDirectory, tileName(parentDepth, parentLongIndex, parentLatIndex)), "PNG", options="optimize")
            if outputAccumulo is not None:
                buff = StringIO.StringIO()
                image.save(buff, "PNG", options="optimize")
                outputAccumulo.stdin.write(json.dumps({"KEY": "%s_%s" % (tileName(parentDepth, parentLongIndex, parentLatIndex), layer), "L2PNG": base64.b64encode(buff.getvalue())}))
                outputAccumulo.stdin.write("\n")

# tiles = {}
# reduce_tiles(tiles, sys.stdin, outputDirectory="/tmp/map-reduce")
# for depth in xrange(10, 1, -1):
#     collate(depth, tiles, outputDirectory="/tmp/map-reduce")

accumulo = subprocess.Popen(["java", "-jar", "/home/export/tanya/matsu-project/Libraries/Accumulo Interface/matsuAccumuloInterface.jar", "write", "quicktest12"], stdin=subprocess.PIPE)

tiles = {}
reduce_tiles(tiles, sys.stdin, outputAccumulo=accumulo)

for depth in xrange(10, 1, -1):
    collate(depth, tiles, outputAccumulo=accumulo)

