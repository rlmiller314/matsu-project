import sys
import glob
import json
import time

import numpy
from PIL import Image
from osgeo import gdal
from osgeo import osr
from osgeo import gdalconst

gdal.UseExceptions()
osr.UseExceptions()

# goodBands = set("B%03d" % b for b in range(10, 40+1) + range(42, 57+1) + range(82, 97+1) + range(102, 120+1) + range(134, 164+1) + range(183, 225+1))
goodBands = set(["B029", "B023", "B016"])

import GeoPictureSerializer
geoPicture = GeoPictureSerializer.GeoPicture()

# for inputDir in ["/mnt/pictures-L1G-TIFF/2010/003/EO1H0790732010003110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/015/EO1H0990612010015110TC_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/080/EO1H0450732010080110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/084/EO1H1430472010084110PF_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/086/EO1H1070592010086110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/096/EO1H2330512010096110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/097/EO1H0210502010097110KF_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/099/EO1H0660732010099110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/101/EO1H1210542010101110T7_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2010/101/EO1H2330512010101110T3_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/007/EO1H0780622011007110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/008/EO1H0850822011008110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/009/EO1H0920762011009110KF_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/162/EO1H0600742011162110T1_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/204/EO1H0480662011204110T2_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/211/EO1H0620462011211110KF_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/219/EO1H0770642011219110T7_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/222/EO1H2330882011222110PF_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/229/EO1H0440752011229110TD_HYP_L1G",
#                  "/mnt/pictures-L1G-TIFF/2011/229/EO1H1320552011229110T2_HYP_L1G"]:

inputDir = sys.argv[1]

# outputFileName = "/mnt/pictures-L1G-serialized" + inputDir[inputDir.index("/EO1H"):] + ".serialized"
# outputFileName = "/mnt/pictures-L1G-serialized/MountEverest" + inputDir[inputDir.index("/EO1H"):] + ".serialized"
outputFileName = "/mnt/pictures-L1G-serialized/GobiDesertWeirdness-RGB" + inputDir[inputDir.index("/EO1H"):] + ".serialized"

print time.time(), inputDir, "->", outputFileName

# convert the NASA-format L1T file into a JSON-formatted string
l1t = {}
try:
    l1tFileName = glob.glob(inputDir + "/*.L1T")[0]
except IndexError:
    print "%s doesn't have a L1T metadata file" % inputDir
else:
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

    tiffs = glob.glob(inputDir + "/EO1H*_B[0-9][0-9][0-9]_L1T.TIF")

    tiffs = dict((t[-12:-8], gdal.Open(t, gdalconst.GA_ReadOnly)) for t in tiffs)
    sampletiff = tiffs.values()[0]

    geoPicture.metadata["GeoTransform"] = json.dumps(sampletiff.GetGeoTransform())
    geoPicture.metadata["Projection"] = sampletiff.GetProjection()

    geoPicture.bands = list(goodBands.intersection(tiffs.keys()))
    geoPicture.bands.sort()

    print "Attempting to serialize %d bands" % len(geoPicture.bands)

    array = numpy.empty((sampletiff.RasterYSize, sampletiff.RasterXSize, len(geoPicture.bands)), dtype=numpy.float)

    print "array.shape", array.shape

    for index, key in enumerate(geoPicture.bands):
        if int(key[1:]) <= 70:
            scaleFactor = 1./float(l1t["RADIANCE_SCALING"]["SCALING_FACTOR_VNIR"])
        else:
            scaleFactor = 1./float(l1t["RADIANCE_SCALING"]["SCALING_FACTOR_SWIR"])

        band = tiffs[key].GetRasterBand(1).ReadAsArray()
        array[:,:,index] = numpy.multiply(band, scaleFactor)

    del tiffs
    del sampletiff

    print "serializing...", time.time()
    geoPicture.picture = array
    geoPicture.serialize(open(outputFileName, "w"))

    print "done", time.time()
