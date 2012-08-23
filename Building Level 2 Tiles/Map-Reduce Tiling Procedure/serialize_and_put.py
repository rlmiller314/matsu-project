#!/usr/bin/env python

import sys
import glob
import json
import argparse
import subprocess
import re

import numpy
from PIL import Image
from osgeo import gdal
from osgeo import osr
from osgeo import gdalconst

HADOOP = "/opt/hadoop/bin/hadoop"

gdal.UseExceptions()
osr.UseExceptions()

parser = argparse.ArgumentParser(description="Glue together a set of image bands with their metadata, serialize, and put the result in HDFS.")
parser.add_argument("inputDirectory", help="local filesystem directory containing TIF and L1T files")
parser.add_argument("outputFilename", help="HDFS filename for the output (make sure the directory exists)")
parser.add_argument("--bands", nargs="+", default=["B029", "B023", "B016"], help="list of bands to retrieve, like \"B029 B023 B016\" for Hyperion or \"B01 B02 B03 B04 B05 B06 B07 B08 B09 B10\" for ALI")
parser.add_argument("--requireAllBands", action="store_true", help="if any bands are missing, skip this image; default is to simply ignore the missing bands and include the others")
parser.add_argument("--toLocalFile", action="store_true", help="save the serialized result to a local file instead of HDFS")
args = parser.parse_args()

import GeoPictureSerializer
geoPicture = GeoPictureSerializer.GeoPicture()

# convert the NASA-format L1T file into a JSON-formatted string
l1t = {}
try:
    # ask for both the Hyperion metadata file and the ALI metadata file; you'll only get one; take the first
    l1tFileName = (glob.glob(args.inputDirectory + "/*.L1T") + glob.glob(args.inputDirectory + "/*_MTL_L1T.TIF"))[0]
except IndexError:
    raise Exception("%s doesn't have a L1T metadata file" % args.inputDirectory)

with open(l1tFileName) as l1tFile:
    last = l1t
    stack = []
    for line in l1tFile.xreadlines():
        if line.rstrip() == "END": break
        name, value = line.rstrip().lstrip().split(" = ")
        value = value.rstrip("\"").lstrip("\"")
        if name == "GROUP":
            stack.append(last)
            last = {}
            l1t[value] = last
        elif name == "END_GROUP":
            last = stack.pop()
        else:                               
            last[name] = value
    geoPicture.metadata["L1T"] = json.dumps(l1t)

tiffs = glob.glob(args.inputDirectory + "/EO1*_B[0-9][0-9]*_L1T.TIF")   # Hyperion band names have three digits, ALI have two

tiffs = dict((re.search("_(B[0-9]+)_", t).group(1), gdal.Open(t, gdalconst.GA_ReadOnly)) for t in tiffs)

for t in tiffs.keys():
    if t not in args.bands:
        del tiffs[t]

try:
    sampletiff = tiffs.values()[0]
except IndexError:
    raise Exception("%s doesn't have any TIFs at all" % args.inputDirectory)

geoPicture.metadata["GeoTransform"] = json.dumps(sampletiff.GetGeoTransform())
geoPicture.metadata["Projection"] = sampletiff.GetProjection()

geoPicture.bands = list(set(args.bands).intersection(tiffs.keys()))
geoPicture.bands.sort()

if args.requireAllBands and len(geoPicture.bands) != len(args.bands):
    raise Exception("%s is missing some of the requested bands and --requireAllBands was specified" % args.inputDirectory)
if len(geoPicture.bands) == 0:
    raise Exception("%s is missing all bands" % args.inputDirectory)

array = numpy.empty((sampletiff.RasterYSize, sampletiff.RasterXSize, len(geoPicture.bands)), dtype=numpy.float)

for index, key in enumerate(geoPicture.bands):
    bandNumber = int(key[1:])

    radianceScaling = l1t["RADIANCE_SCALING"]
    if "SCALING_FACTOR_VNIR" in radianceScaling:   # if Hyperion:
        scaleOffset = 0.
        if bandNumber <= 70:
            scaleFactor = 1./float(radianceScaling["SCALING_FACTOR_VNIR"])
        else:
            scaleFactor = 1./float(radianceScaling["SCALING_FACTOR_SWIR"])

    else:   # else ALI:
        scaleOffset = 0.
        scaleFactor = 1./300.  # from the EO-1 User Guide Version 2.3, FAQ on ALI

        ### According to (my uncertain reading of) the User Guide, these corrections were already applied in the Level-0 to Level-1 step:
        # scaleOffset = float(radianceScaling["BAND%d_OFFSET" % bandNumber])
        # scaleFactor = 1./float(radianceScaling["BAND%d_SCALING_FACTOR" % bandNumber])

    band = tiffs[key].GetRasterBand(1).ReadAsArray()
    array[:,:,index] = (band * scaleFactor) + scaleOffset

geoPicture.picture = array

if args.toLocalFile:
    output = open(args.outputFilename, "w")
    geoPicture.serialize(output)
    output.write("\n")
else:
    hadoop = subprocess.Popen([HADOOP, "dfs", "-put", "-", args.outputFilename], stdin=subprocess.PIPE)
    geoPicture.serialize(hadoop.stdin)
    hadoop.stdin.write("\n")
