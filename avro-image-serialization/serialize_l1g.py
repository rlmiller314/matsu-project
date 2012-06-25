import glob

import numpy
from PIL import Image
from osgeo import gdal
from osgeo import osr
from osgeo import gdalconst

gdal.UseExceptions()
osr.UseExceptions()

# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/003/EO1H0790732010003110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/015/EO1H0990612010015110TC_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/080/EO1H0450732010080110T2_HYP_L1G"
BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/084/EO1H1430472010084110PF_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/086/EO1H1070592010086110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/096/EO1H2330512010096110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/097/EO1H0210502010097110KF_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/099/EO1H0660732010099110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/101/EO1H1210542010101110T7_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2010/101/EO1H2330512010101110T3_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/007/EO1H0780622011007110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/008/EO1H0850822011008110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/009/EO1H0920762011009110KF_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/162/EO1H0600742011162110T1_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/204/EO1H0480662011204110T2_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/211/EO1H0620462011211110KF_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/219/EO1H0770642011219110T7_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/222/EO1H2330882011222110PF_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/229/EO1H0440752011229110TD_HYP_L1G"
# BASE_DIRECTORY = "/mnt/pictures-L1G-TIFF/2011/229/EO1H1320552011229110T2_HYP_L1G"

tiffs = glob.glob(BASE_DIRECTORY + "/EO1H*_B[0-9][0-9][0-9]_L1T.TIF")

tiffs = dict((t[-12:-8], gdal.Open(t, gdalconst.GA_ReadOnly)) for t in tiffs)

sampletiff = tiffs.values()[0]

print sampletiff.RasterYSize, sampletiff.RasterXSize, len(tiffs), numpy.empty(1, dtype=numpy.float).itemsize

array = numpy.empty((sampletiff.RasterYSize, sampletiff.RasterXSize, len(tiffs)), dtype=numpy.float)

keys = tiffs.keys()
keys.sort()
for index, key in enumerate(keys):
    if int(key[1:]) <= 70:
        scaleFactor = 1./40.
    else:
        scaleFactor = 1./80.

    band = tiffs[key].GetRasterBand(1).ReadAsArray()
    array[:,:,index] = numpy.multiply(band, scaleFactor)

    print index

print array

# image = Image.fromarray(array)
# image.save("/var/www/quick-look/tmp.png", "PNG", option="optimize")
