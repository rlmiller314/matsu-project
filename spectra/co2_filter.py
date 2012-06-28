import re
import glob
import random
from math import *

import numpy
from PIL import Image
from osgeo import gdal
from osgeo import gdalconst

from cassius import *

gdal.UseExceptions()

# directory = "/mnt/pictures-L1G-TIFF/AtacamaDesert/EO1H2320822012070110P1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/AtacamaDesert/EO1H2330762011007110K3_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/AtacamaDesert/EO1H2330752011243110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/AustralianOutback/EO1H1120762010087110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672011201110P0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672011206110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012041110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012049110P0_HYP_L1G"  # maybe
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012067110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012075110P0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012088110K1_HYP_L1G"   # water vapor spots
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012096110P0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/DeforestedAmazon/EO1H2310672012161110K1_HYP_L1G"   # CO2 slightly higher over deforested parts?
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622011216110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622011221110P1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012090110P1_HYP_L1G"
directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012124110P1_HYP_L1G"    # definitely anticorrelated with water
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012129110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012132110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012137110P1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012145110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012166110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/ForestedAmazon/EO1H2270622012171110P1_HYP_L1G"
directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H0672282012138110KF_HYP_L1G"   # some good spots
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H0672282012146110KF_HYP_L1G"   # meh
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H2180152010091110PF_HYP_L1G"   # missing B186
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H2180152010096110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H2180152010098110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H2180152011263110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/IcelandicVolcano/EO1H2180152012164110KF_HYP_L1G"    # spots are not exactly in the same spots
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812010100110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812011016110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812011169110K0_HYP_L1G"  # lots of salt
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012048110P1_HYP_L1G"  # still lots of salt  THIS IS WHAT I USED FOR THE SPECTRUM
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012069110K0_HYP_L1G"  # all water
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012082110K0_HYP_L1G"  # still all water
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012113110K1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012129110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012134110P1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/LakeFrome/EO1H0970812012155110K0_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H0260472011004110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H0260472011190110PF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H0260472012116110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H0260472012124110PF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H0260472012155110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H1291972012147110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H1291972012150110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MexicoCity/EO1H1291972012155110PF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MountEverest/EO1H1400402011243110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MountEverest/EO1H1400402012131110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MountEverest/EO1H1400402012144110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MountEverest/EO1H1400402012159110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/MountEverest/EO1H1400412011010110KF_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150322011201110K3_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332011007110T2_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332011209110P7_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012070110T2_HYP_L1G"   # this one has all the necessary bands, but it's nighttime
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012075110T3_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012083110T2_HYP_L1G"   # this works, too, though the bottom part of the input image has weird features
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012088110T4_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012091110T1_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012096110T3_HYP_L1G"    # best so far
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012122110KY_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012125110KW_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012143110KB_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012151110KX_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012159110KW_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012164110P7_HYP_L1G"
# directory = "/mnt/pictures-L1G-TIFF/WashingtonDC/EO1H0150332012172110KA_HYP_L1G"

B029 = gdal.Open(glob.glob(directory + ("/*_B029_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B023 = gdal.Open(glob.glob(directory + ("/*_B023_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B016 = gdal.Open(glob.glob(directory + ("/*_B016_L1T.TIF"))[0], gdalconst.GA_ReadOnly)

B029 = B029.GetRasterBand(1).ReadAsArray()
B023 = B023.GetRasterBand(1).ReadAsArray()
B016 = B016.GetRasterBand(1).ReadAsArray()

alpha = B029 > 0
numpy.logical_and(alpha, B023 > 0, alpha)
numpy.logical_and(alpha, B016 > 0, alpha)
alpha = numpy.array(alpha, dtype=numpy.uint8) * 255

minvalue = min(B029.min(), B023.min(), B016.min())
maxvalue = max(B029.max(), B023.max(), B016.max())

for array in B029, B023, B016:
    numpy.subtract(array, minvalue, array)
    numpy.multiply(array, 255./(maxvalue - minvalue), array)
    array.dtype = numpy.uint8
B029 = B029[:,::2]
B023 = B023[:,::2]
B016 = B016[:,::2]

image = Image.fromarray(numpy.dstack((B029, B023, B016, alpha)))
image.save("/var/www/quick-look/tmp2.png", "PNG", option="optimized")

# Get the ten bands relevant for carbon dioxide

B183 = gdal.Open(glob.glob(directory + ("/*_B183_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B184 = gdal.Open(glob.glob(directory + ("/*_B184_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B185 = gdal.Open(glob.glob(directory + ("/*_B185_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B186 = gdal.Open(glob.glob(directory + ("/*_B186_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B188 = gdal.Open(glob.glob(directory + ("/*_B188_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B189 = gdal.Open(glob.glob(directory + ("/*_B189_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B190 = gdal.Open(glob.glob(directory + ("/*_B190_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B191 = gdal.Open(glob.glob(directory + ("/*_B191_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B194 = gdal.Open(glob.glob(directory + ("/*_B194_L1T.TIF"))[0], gdalconst.GA_ReadOnly)
B195 = gdal.Open(glob.glob(directory + ("/*_B195_L1T.TIF"))[0], gdalconst.GA_ReadOnly)

B183 = B183.GetRasterBand(1).ReadAsArray() / 80.
B184 = B184.GetRasterBand(1).ReadAsArray() / 80.
B185 = B185.GetRasterBand(1).ReadAsArray() / 80.
B186 = B186.GetRasterBand(1).ReadAsArray() / 80.
B188 = B188.GetRasterBand(1).ReadAsArray() / 80.
B189 = B189.GetRasterBand(1).ReadAsArray() / 80.
# B190 = B190.GetRasterBand(1).ReadAsArray() / 80.
# B191 = B191.GetRasterBand(1).ReadAsArray() / 80.
# B194 = B194.GetRasterBand(1).ReadAsArray() / 80.
# B195 = B195.GetRasterBand(1).ReadAsArray() / 80.

# Work in the log-radiance space (and offset zeros by a tenth of a resolution unit)
numpy.add(B183, 0.1/80., B183);  numpy.log(B183, B183)
numpy.add(B184, 0.1/80., B184);  numpy.log(B184, B184)
numpy.add(B185, 0.1/80., B185);  numpy.log(B185, B185)
numpy.add(B186, 0.1/80., B186);  numpy.log(B186, B186)
numpy.add(B188, 0.1/80., B188);  numpy.log(B188, B188)
numpy.add(B189, 0.1/80., B189);  numpy.log(B189, B189)
# numpy.add(B190, 0.1/80., B190);  numpy.log(B190, B190)
# numpy.add(B191, 0.1/80., B191);  numpy.log(B191, B191)
# numpy.add(B194, 0.1/80., B194);  numpy.log(B194, B194)
# numpy.add(B195, 0.1/80., B195);  numpy.log(B195, B195)

# Linear-fit the background bands (B183, B184, B188, B189, B194, B195)

# # the first three are just numbers
# sum1 = 6.
# sumx = 183. + 184. + 188. + 189. + 194. + 195.
# sumxx = 183.**2 + 184.**2 + 188.**2 + 189.**2 + 194.**2 + 195.**2
# # the last two are images (2-D arrays)
# sumy = B183 + B184 + B188 + B189 + B194 + B195
# sumxy = 183.*B183 + 184.*B184 + 188.*B188 + 189.*B189 + 194.*B194 + 195.*B195

# the first three are just numbers
sum1 = 4.
sumx = 183. + 184. + 188. + 189.
sumxx = 183.**2 + 184.**2 + 188.**2 + 189.**2
# the last two are images (2-D arrays)
sumy = B183 + B184 + B188 + B189
sumxy = 183.*B183 + 184.*B184 + 188.*B188 + 189.*B189

delta = sum1*sumxx - sumx**2
constant = (sumxx*sumy - sumx*sumxy) / delta
linear = (sum1*sumxy - sumx*sumy) / delta

# How high are the peaks above the linear background?
firstpeak = (B185 - (constant + 185.*linear))/2. + (B186 - (constant + 186.*linear))/2.
# secondpeak = (B190 - (constant + 190.*linear))/2. + (B191 - (constant + 191.*linear))/2.

# Negate it (because they're absorbtion peaks)

red = numpy.exp(-firstpeak)
# green = -secondpeak + log(4.)

minvalue = red.min()  # minvalue = min(red.min(), green.min())
maxvalue = red.max()  # maxvalue = max(red.max(), green.max())

red = numpy.array((red - minvalue) * 255./(maxvalue - minvalue), dtype=numpy.uint8)
# green = numpy.array((green - minvalue) * 255./(maxvalue - minvalue), dtype=numpy.uint8)
green = numpy.zeros(red.shape, dtype=numpy.uint8)
blue = numpy.zeros(red.shape, dtype=numpy.uint8)

image = Image.fromarray(numpy.dstack((red, green, blue, alpha)))
image.save("/var/www/quick-look/tmp3.png", "PNG", option="optimized")
