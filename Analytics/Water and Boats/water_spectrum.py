from math import *
import glob

import numpy
from PIL import Image
from osgeo import gdal
from osgeo import gdalconst

from cassius import *

#####################################################################################

inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011197110KF_HYP_L1G"
# inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011210110KF_HYP_L1G"
# inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011205110PF_HYP_L1G"

red = gdal.Open(glob.glob(inputDir + "/*_B029_L1T.TIF")[0], gdalconst.GA_ReadOnly)
green = gdal.Open(glob.glob(inputDir + "/*_B023_L1T.TIF")[0], gdalconst.GA_ReadOnly)
blue = gdal.Open(glob.glob(inputDir + "/*_B016_L1T.TIF")[0], gdalconst.GA_ReadOnly)

red = red.GetRasterBand(1).ReadAsArray() / 40.
green = green.GetRasterBand(1).ReadAsArray() / 40.
blue = blue.GetRasterBand(1).ReadAsArray() / 40.

red = red[2200:2800,197:358]
green = green[2200:2800,197:358]
blue = blue[2200:2800,197:358]

mincut = 5.
maxcut = 95.
minvalue = min(numpy.percentile(red[red > 10.], mincut), numpy.percentile(green[green > 10.], mincut), numpy.percentile(blue[blue > 10.], mincut))
maxvalue = max(numpy.percentile(red[red > 10.], maxcut), numpy.percentile(green[green > 10.], maxcut), numpy.percentile(blue[blue > 10.], maxcut))

red = numpy.array(numpy.maximum(numpy.minimum((red - minvalue) / (maxvalue - minvalue) * 255., 255), 0), dtype=numpy.uint8)
green = numpy.array(numpy.maximum(numpy.minimum((green - minvalue) / (maxvalue - minvalue) * 255., 255), 0), dtype=numpy.uint8)
blue = numpy.array(numpy.maximum(numpy.minimum((blue - minvalue) / (maxvalue - minvalue) * 255., 255), 0), dtype=numpy.uint8)

image = numpy.dstack((red, green, blue))
image = Image.fromarray(image)
image.show()
image.save("high_contrast_fragment.png", "PNG", options="optimize")

#####################################################################################

def wavelength(bandNumber):
    if bandNumber < 70.5:
        return (bandNumber - 10.) * 10.213 + 446.
    else:
        return (bandNumber - 79.) * 10.110 + 930.

masks = {}
for mask in "cloud-shadow", "pure-water", "image-defect", "clouds-loose", "clouds-tight", "wake-loose", "wake-tight":
    masks[mask] = Image.open(open("mask_%s.png" % mask))
    masks[mask] = (numpy.array(masks[mask])[:,:,1] < 128)

# maskNumPixels = {}
# for mask in masks:
#     maskNumPixels[mask] = numpy.count_nonzero(masks[mask])

#####################################################################################

intensity = {}
variationup = {}
variationdown = {}
for bandNumber in xrange(1, 242+1):
    data = glob.glob(inputDir + "/*_B%03d_L1T.TIF" % bandNumber)
    if len(data) == 0: continue
    data = gdal.Open(data[0], gdalconst.GA_ReadOnly)
    if bandNumber < 70.5:
        data = data.GetRasterBand(1).ReadAsArray() / 40.
    else:
        data = data.GetRasterBand(1).ReadAsArray() / 80.
    data = data[2200:2800,197:358]
    if data.mean() < 0.1: continue
    print bandNumber
    for mask in masks:
        maskedData = data[masks[mask]]
        mean = maskedData.mean()
        stdev = sqrt(maskedData.var())
        try:
            intensity[bandNumber, mask] = log(mean)
            variationup[bandNumber, mask] = log(mean + stdev) - log(mean)
            variationdown[bandNumber, mask] = log(mean - stdev) - log(mean)
        except ValueError:
            intensity.pop((bandNumber, mask), None)
            variationup.pop((bandNumber, mask), None)
            variationdown.pop((bandNumber, mask), None)

keys = intensity.keys()
keys.sort()

plots = {}
for mask in masks:
    plots[mask] = Scatter(x=[wavelength(bandNumber) for bandNumber, m in keys if m == mask], y=[intensity[bandNumber, m] for bandNumber, m in keys if m == mask], ey=[variationup[bandNumber, m] for bandNumber, m in keys if m == mask], eyl=[variationdown[bandNumber, m] for bandNumber, m in keys if m == mask], connector="xsort")

plots["pure-water"].linecolor = "blue"
plots["pure-water"].markercolor = "blue"

plots["wake-tight"].linecolor = "black"
plots["wake-tight"].markercolor = "black"

plots["clouds-tight"].linecolor = "red"
plots["clouds-tight"].markercolor = "red"

selctedbands = Grid(vert=map(wavelength, [16, 150]), linecolor="darkgreen", linewidth=2., linestyle="solid")

legend = Legend([[plots["clouds-tight"], "clouds"], [plots["wake-tight"], "wake of ship"], [plots["pure-water"], "water"], [selctedbands, "bands 16, 150"]], colwid=[0.3, 0.7], justify="cl", width=0.37)

view(Overlay(selctedbands, plots["pure-water"], plots["wake-tight"], plots["clouds-tight"], legend, xmin=450., xmax=2400., xlabel="wavelength [nm]", ylabel="log(radiance) [log(W/m/m/sr/micron)]"), fileName="plots_threespectra.svg")

#####################################################################################

image016 = gdal.Open(glob.glob(inputDir + "/*_B%03d_L1T.TIF" % 16)[0], gdalconst.GA_ReadOnly)
image150 = gdal.Open(glob.glob(inputDir + "/*_B%03d_L1T.TIF" % 150)[0], gdalconst.GA_ReadOnly)

image016 = image016.GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 40.
image150 = image150.GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 80.

water = zip(image016[masks["pure-water"]], image150[masks["pure-water"]])
wake = zip(image016[masks["wake-tight"]], image150[masks["wake-tight"]])
clouds = zip(image016[masks["clouds-tight"]], image150[masks["clouds-tight"]])

waterplot = Scatter(water, sig=["x", "y"], limit=1000, markercolor="blue")
wakeplot = Scatter(wake, sig=["x", "y"], limit=1000, markercolor="black")
cloudsplot = Scatter(clouds, sig=["x", "y"], limit=1000, markercolor="red")

origin, xscale, xbasis, yscale, ybasis = principleComponents(numpy.array(water))
waterellipse = Scatter(
    x=[origin[0] + xscale*xbasis[0]*cos(t) + yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + xscale*xbasis[1]*cos(t) + yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None)
waterellipse2 = Scatter(
    x=[origin[0] + 2.*xscale*xbasis[0]*cos(t) + 2.*yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + 2.*xscale*xbasis[1]*cos(t) + 2.*yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None, linestyle="dashed")

origin, xscale, xbasis, yscale, ybasis = principleComponents(numpy.array(wake))
wakeellipse = Scatter(
    x=[origin[0] + xscale*xbasis[0]*cos(t) + yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + xscale*xbasis[1]*cos(t) + yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None)
wakeellipse2 = Scatter(
    x=[origin[0] + 2.*xscale*xbasis[0]*cos(t) + 2.*yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + 2.*xscale*xbasis[1]*cos(t) + 2.*yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None, linestyle="dashed")

origin, xscale, xbasis, yscale, ybasis = principleComponents(numpy.array(clouds))
cloudsellipse = Scatter(
    x=[origin[0] + xscale*xbasis[0]*cos(t) + yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + xscale*xbasis[1]*cos(t) + yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None)
cloudsellipse2 = Scatter(
    x=[origin[0] + 2.*xscale*xbasis[0]*cos(t) + 2.*yscale*ybasis[0]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)],
    y=[origin[1] + 2.*xscale*xbasis[1]*cos(t) + 2.*yscale*ybasis[1]*sin(t) for t in numpy.arange(0., 2.*pi + 0.1, 0.1)], connector="unsorted", marker=None, linestyle="dashed")

legend = Legend([[cloudsplot, "clouds"], [wakeplot, "wake of ship"], [waterplot, "water"], [waterellipse, "PCA analysis"], [waterellipse2, "PCA 2 sigma"]], colwid=[0.3, 0.7], justify="cl", width=0.37)

view(Overlay(waterplot, wakeplot, cloudsplot, waterellipse, wakeellipse, cloudsellipse, waterellipse2, wakeellipse2, cloudsellipse2, legend, xlabel="band 16 radiance [W/m/m/sr/micron]", ylabel="band 150 radiance [W/m/m/sr/micron]", xmin=0., xmax=300., ymin=0., ymax=35.), fileName="plots_justtwobands.svg")
