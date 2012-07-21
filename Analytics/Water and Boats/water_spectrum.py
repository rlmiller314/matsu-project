from math import *
import glob
import random
import time

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

#####################################################################################

water = numpy.zeros(242, dtype=numpy.float)

waters = []
for pixelNumber in xrange(1000):
    waters.append(numpy.zeros(242, dtype=numpy.float))

wakes = []
for pixelNumber in xrange(numpy.count_nonzero(masks["wake-tight"])):
    wakes.append(numpy.zeros(242, dtype=numpy.float))

clouds = []
for pixelNumber in xrange(numpy.count_nonzero(masks["clouds-tight"])):
    clouds.append(numpy.zeros(242, dtype=numpy.float))

bands = []
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
    water[len(bands)] = log(data[masks["pure-water"]].mean())
    for w, v in zip(waters, data[masks["pure-water"]][:1000]):
        w[len(bands)] = log(v + 1e-10)
    for w, v in zip(wakes, data[masks["wake-tight"]]):
        w[len(bands)] = log(v + 1e-10)
    for w, v in zip(clouds, data[masks["clouds-tight"]]):
        w[len(bands)] = log(v + 1e-10)
    bands.append(bandNumber)

sampleBands = [40, 54, 99, 110, 131, 155]

# view(Scatter(x=bands, y=water[:len(bands)], marker=None, connector="unsorted"))
view(Overlay(Grid(vert=map(wavelength, sampleBands)), Scatter(x=map(wavelength, bands), y=water[:len(bands)], marker=None, connector="unsorted"), Legend([[Style(linecolor="black"), "water"], [Grid(), "6 sample bands"]], colwid=[0.3, 0.7], justify="cl", width=0.45), xmin=450., xmax=2400., xlabel="wavelength [nm]", ylabel="log(radiance) [log(W/m/m/sr/micron)]"), fileName="plot_water_samplebands.svg")

# view(Overlay(*([Grid(vert=map(wavelength, sampleBands))] + [Scatter(x=map(wavelength, bands), y=(w[:len(bands)] - w[:len(bands)].mean()), marker=None, connector="unsorted", linecolor=c) for w, c in zip(random.sample(waters, 20), darkseries(20))]), xmin=450., xmax=2400.))

# for w in wakes:
#     view(Scatter(x=bands, y=(w[:len(bands)] - water[:len(bands)]), marker=None, connector="unsorted", ymin=-3., ymax=3.))
#     time.sleep(0.1)

# view(Overlay(*[Scatter(x=map(wavelength, bands), y=(w[:len(bands)] - water[:len(bands)] - w[:len(bands)].mean()), marker=None, connector="unsorted", linecolor=c) for w, c in zip(random.sample(wakes, 20), darkseries(20))]))

view(Overlay(*([Grid(vert=map(wavelength, sampleBands))] + [Scatter(x=map(wavelength, bands), y=(w[:len(bands)] - water[:len(bands)] - w[:len(bands)].mean()), marker=None, connector="unsorted", linecolor=c) for w, c in zip(random.sample(wakes, 20), darkseries(20))] + [Legend([[Style(linecolor="red"), "wake/water"], [Grid(), "6 sample bands"]], colwid=[0.3, 0.7], justify="cl", width=0.45)]), xmin=450., xmax=2400., ymax=3.), xlabel="wavelength [nm]", ylabel="log(normalized wake radiance / water radiance)", fileName="plot_wake_samplebands.svg")

# for w in clouds:
#     view(Scatter(x=bands, y=(w[:len(bands)] - water[:len(bands)]), marker=None, connector="unsorted", ymin=-3., ymax=5.))
#     time.sleep(0.1)

# view(Overlay(*([Grid(vert=map(wavelength, sampleBands))] + [Scatter(x=map(wavelength, bands), y=(w[:len(bands)] - water[:len(bands)] - w[:len(bands)].mean()), marker=None, connector="unsorted", linecolor=c) for w, c in zip(random.sample(clouds, 20), darkseries(20))]), xmin=450., xmax=2400.))

view(Overlay(*([Grid(vert=map(wavelength, sampleBands))] + [Scatter(x=map(wavelength, bands), y=(w[:len(bands)] - water[:len(bands)] - w[:len(bands)].mean()), marker=None, connector="unsorted", linecolor=c) for w, c in zip(random.sample(clouds, 20), darkseries(20))] + [Legend([[Style(linecolor="red"), "cloud/water"], [Grid(), "6 sample bands"]], colwid=[0.3, 0.7], justify="cl", width=0.45)]), xmin=450., xmax=2400., ymax=3.5), xlabel="wavelength [nm]", ylabel="log(normalized cloud radiance / water radiance)", fileName="plot_cloud_samplebands.svg")

view(Overlay(*([Grid(vert=map(wavelength, sampleBands))] + [Scatter(x=map(wavelength, bands), y=((w1[:len(bands)] - w1[:len(bands)].mean()) - (w2[:len(bands)] - w2[:len(bands)].mean())), marker=None, connector="unsorted", linecolor=c) for w1, w2, c in zip(random.sample(wakes, 20), random.sample(clouds, 20), darkseries(20))] + [Legend([[Style(linecolor="red"), "wake/cloud"], [Grid(), "6 sample bands"]], colwid=[0.3, 0.7], justify="cl", width=0.45)]), xmin=450., xmax=2400.), xlabel="wavelength [nm]", ylabel="log(normalized wake radiance / normalized cloud radiance)", fileName="plot_wakes_clouds_samplebands.svg")

#####################################################################################

images = {}
for band in sampleBands:
    images[band] = gdal.Open(glob.glob(inputDir + "/*_B%03d_L1T.TIF" % band)[0], gdalconst.GA_ReadOnly)
    if band < 70.5:
        images[band] = images[band].GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 40.
    else:
        images[band] = images[band].GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 80.

plots = {}
for i in xrange(len(sampleBands)):
    for j in xrange(i+1, len(sampleBands)):
        watery = zip(numpy.log(images[sampleBands[i]][masks["pure-water"]] + 1e-10), numpy.log(images[sampleBands[j]][masks["pure-water"]] + 1e-10))
        wake = zip(numpy.log(images[sampleBands[i]][masks["wake-tight"]] + 1e-10), numpy.log(images[sampleBands[j]][masks["wake-tight"]] + 1e-10))
        clouds = zip(numpy.log(images[sampleBands[i]][masks["clouds-tight"]] + 1e-10), numpy.log(images[sampleBands[j]][masks["clouds-tight"]] + 1e-10))

        waterplot = Scatter(watery, sig=["x", "y"], limit=1000, markercolor="blue")
        wakeplot = Scatter(wake, sig=["x", "y"], limit=1000, markercolor="black")
        cloudsplot = Scatter(clouds, sig=["x", "y"], limit=1000, markercolor="red")

        plots[i,j] = Overlay(waterplot, wakeplot, cloudsplot, xlabel="log(band %d)" % sampleBands[i], ylabel="log(band %d)" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15, xmin=-5., ymin=-5., xmax=6., ymax=6.)

view(Layout(5, 5,
            None,       None,       None,       None,       plots[0,1],
            None,       None,       None,       plots[1,2], plots[0,2],
            None,       None,       plots[2,3], plots[1,3], plots[0,3],
            None,       plots[3,4], plots[2,4], plots[1,4], plots[0,4],
            plots[4,5], plots[3,5], plots[2,5], plots[1,5], plots[0,5]), width=2500, height=2500, fileName="plot_log6x6grid.svg")
