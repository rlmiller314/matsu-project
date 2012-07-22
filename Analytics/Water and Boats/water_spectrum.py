from math import *
import glob
import random
import time

import numpy
from scipy.stats import chi2 as chi2prob
from PIL import Image
from osgeo import gdal
from osgeo import gdalconst

from cassius import *
from minuit import Minuit

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

original_images = {}
for i, band in enumerate(sampleBands):
    original_images[band] = gdal.Open(glob.glob(inputDir + "/*_B%03d_L1T.TIF" % band)[0], gdalconst.GA_ReadOnly)
    if band < 70.5:
        original_images[band] = original_images[band].GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 40.
    else:
        original_images[band] = original_images[band].GetRasterBand(1).ReadAsArray()[2200:2800,197:358] / 80.

images = numpy.dstack([original_images[sampleBands[i]] for i in xrange(len(sampleBands))])
del original_images

plots = {}
logplots = {}
for i in xrange(len(sampleBands)):
    for j in xrange(i+1, len(sampleBands)):
        watery = zip(images[:,:,i][masks["pure-water"]], images[:,:,j][masks["pure-water"]])
        wake = zip(images[:,:,i][masks["wake-tight"]], images[:,:,j][masks["wake-tight"]])
        clouds = zip(images[:,:,i][masks["clouds-tight"]], images[:,:,j][masks["clouds-tight"]])

        waterplot = Scatter(watery, sig=["x", "y"], limit=1000, markercolor="blue")
        wakeplot = Scatter(wake, sig=["x", "y"], limit=1000, markercolor="black")
        cloudsplot = Scatter(clouds, sig=["x", "y"], limit=1000, markercolor="red")

        plots[i,j] = Overlay(waterplot, wakeplot, cloudsplot, xlabel="band %d" % sampleBands[i], ylabel="band %d" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15)

        watery = zip(numpy.log(images[:,:,i][masks["pure-water"]] + 1e-10), numpy.log(images[:,:,j][masks["pure-water"]] + 1e-10))
        wake = zip(numpy.log(images[:,:,i][masks["wake-tight"]] + 1e-10), numpy.log(images[:,:,j][masks["wake-tight"]] + 1e-10))
        clouds = zip(numpy.log(images[:,:,i][masks["clouds-tight"]] + 1e-10), numpy.log(images[:,:,j][masks["clouds-tight"]] + 1e-10))

        waterplot = Scatter(watery, sig=["x", "y"], limit=1000, markercolor="blue")
        wakeplot = Scatter(wake, sig=["x", "y"], limit=1000, markercolor="black")
        cloudsplot = Scatter(clouds, sig=["x", "y"], limit=1000, markercolor="red")

        logplots[i,j] = Overlay(waterplot, wakeplot, cloudsplot, xlabel="log(band %d)" % sampleBands[i], ylabel="log(band %d)" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15, xmin=-5., ymin=-5., xmax=6., ymax=6.)

watercenter = numpy.median(images[masks["pure-water"]], axis=0)
wakecenter = numpy.median(images[masks["wake-tight"]], axis=0)
cloudscenter = numpy.median(images[masks["clouds-tight"]], axis=0)

plotz = {}
for i, j in plots:
    plotz[i,j] = Overlay(plots[i,j], Scatter(x=[watercenter[i], wakecenter[i], cloudscenter[i]], y=[watercenter[j], wakecenter[j], cloudscenter[j]], marker="plus", markercolor="white", markersize=2.), xlabel=plots[i,j].xlabel, ylabel=plots[i,j].ylabel, bottommargin=plots[i,j].bottommargin, leftmargin=plots[i,j].leftmargin, xlabeloffset=plots[i,j].xlabeloffset, ylabeloffset=plots[i,j].ylabeloffset)

view(Layout(5, 5,
            None,       None,       None,       None,       plotz[0,1],
            None,       None,       None,       plotz[1,2], plotz[0,2],
            None,       None,       plotz[2,3], plotz[1,3], plotz[0,3],
            None,       plotz[3,4], plotz[2,4], plotz[1,4], plotz[0,4],
            plotz[4,5], plotz[3,5], plotz[2,5], plotz[1,5], plotz[0,5]), width=2500, height=2500, fileName="plot_6x6grid.svg")

view(Layout(5, 5,
            None,          None,          None,          None,          logplots[0,1],
            None,          None,          None,          logplots[1,2], logplots[0,2],
            None,          None,          logplots[2,3], logplots[1,3], logplots[0,3],
            None,          logplots[3,4], logplots[2,4], logplots[1,4], logplots[0,4],
            logplots[4,5], logplots[3,5], logplots[2,5], logplots[1,5], logplots[0,5]), width=2500, height=2500, fileName="plot_log6x6grid.svg")

#####################################################################################

for i in xrange(len(sampleBands)):
    images[:,:,i] -= watercenter[i]

cloudscenter = numpy.median(images[masks["clouds-tight"]], axis=0)

print cloudscenter
# [ 68.75    45.35     9.4375  27.6125   5.125   14.475 ]

def gramSchmidt(vs):
    us = []
    for i, v in enumerate(vs):
        u = numpy.array(v)
        for j in xrange(i):
            u -= us[j].dot(v) * us[j]
        u /= numpy.linalg.norm(u)
        us.append(u)
    return us

basis = gramSchmidt([cloudscenter] + zip(*numpy.random.randn(6, 5)))
projection = lambda x: sum([ow * ow.dot(x) for ow in basis[1:]])

watery = numpy.array(map(projection, images[masks["pure-water"]]))
wake = numpy.array(map(projection, images[masks["wake-tight"]]))
clouds = numpy.array(map(projection, images[masks["clouds-tight"]]))
everything = numpy.array(map(projection, numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))))
wakeloose = numpy.array(map(projection, images[masks["wake-loose"]]))

plots = {}
for i in xrange(len(sampleBands)):
    for j in xrange(i+1, len(sampleBands)):
        waterplot = Scatter(x=watery[:,i], y=watery[:,j], limit=1000, markercolor="blue")
        wakeplot = Scatter(x=wake[:,i], y=wake[:,j], limit=1000, markercolor="black")
        cloudsplot = Scatter(x=clouds[:,i], y=clouds[:,j], limit=1000, markercolor="red")

        plots[i,j] = Overlay(cloudsplot, waterplot, wakeplot, xlabel="band %d" % sampleBands[i], ylabel="band %d" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15)

view(Layout(5, 5,
            None,       None,       None,       None,       plots[0,1],
            None,       None,       None,       plots[1,2], plots[0,2],
            None,       None,       plots[2,3], plots[1,3], plots[0,3],
            None,       plots[3,4], plots[2,4], plots[1,4], plots[0,4],
            plots[4,5], plots[3,5], plots[2,5], plots[1,5], plots[0,5]), width=2500, height=2500, fileName="plot_6x6grid_cloudsremoved.svg")

def takeALook(band, minvalue=None, maxvalue=None, fileName=None, projection=None):
    if projection is None:
        pictures = images
    else:
        pictures = numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))
        pictures = numpy.array(map(projection, pictures))
        pictures = numpy.reshape(pictures, (images.shape[0], images.shape[1], images.shape[2]))

    onlyBand = pictures[:,:,sampleBands.index(band)]

    if minvalue is None:
        minvalue = numpy.percentile(onlyBand, 5.)
    if maxvalue is None:
        maxvalue = numpy.percentile(onlyBand, 95.)

    onlyBand = numpy.array(numpy.maximum(numpy.minimum((onlyBand - minvalue) / (maxvalue - minvalue) * 255., 255), 0), dtype=numpy.uint8)

    image = numpy.dstack((onlyBand, onlyBand, onlyBand))
    image = Image.fromarray(image)
    if fileName is None:
        image.show()
    else:
        image.save(fileName, "PNG", options="optimized")

takeALook(40)
takeALook(40, 1., 10., projection=projection)

takeALook(40, fileName="cloud_removal_before.png")
takeALook(40, 1., 10., fileName="cloud_removal_after.png", projection=projection)

#####################################################################################

# fakedata = numpy.array([(x, y + 3.*x) for x, y in numpy.random.randn(1000, 2)])
# eigenvalues, eigenvectors = numpy.linalg.eig(numpy.cov(fakedata.T))

# def unitGaussian(p0, p1):
#     return exp(-(p0**2 + p1**2))

# def likelihood(p0, p1):
#     return unitGaussian(*(numpy.array(numpy.matrix([[p0, p1]]) * eigenvectors).flatten() / numpy.sqrt(eigenvalues)))

# colorField = ColorField(100, -6., 6., 100, -6., 6., zmin=-0.1, zmax=1.1)
# colorField.map(likelihood)

# view(Overlay(0, colorField, Scatter(x=fakedata[:,0], y=fakedata[:,1], markersize=0.5)))

#####################################################################################

eigenvalues, eigenvectors = numpy.linalg.eig(numpy.cov(everything.T))
smallestIndex = numpy.argsort(eigenvalues)[0]
eigenvalues[smallestIndex] = 1e10

def likelihood(p0, p1, p2, p3, p4, p5):
    return exp(-sum(numpy.square(numpy.array(numpy.matrix([[p0, p1, p2, p3, p4, p5]]) * eigenvectors).flatten()) / eigenvalues))

# colorField = ColorField(100, -8., 8., 100, -8., 8., zmin=-0.1, zmax=1.1, tocolor=gradients["blues"])
# colorField.map(lambda a, b: likelihood(0., 0., a, b, 0., 0.))

# view(Overlay(0, colorField, Scatter(x=everything[:,2], y=everything[:,3], markersize=0.25, markercolor="red")))

plots = {}
for i in xrange(len(sampleBands)):
    for j in xrange(i+1, len(sampleBands)):
        xmin = min(wake[:,i].min(), everything[:,i].min(), watery[:,i].min())
        xmax = max(wake[:,i].max(), everything[:,i].max(), watery[:,i].max())
        ymin = min(wake[:,j].min(), everything[:,j].min(), watery[:,j].min())
        ymax = max(wake[:,j].max(), everything[:,j].max(), watery[:,j].max())

        wakeplot = Scatter(x=wake[:,i], y=wake[:,j], limit=1000, markercolor="blue", markeroutline="white")

        colorField = ColorField(30, xmin, xmax, 30, ymin, ymax, zmin=-0.1, zmax=1.1, tocolor=gradients["fire"], xlabel="band %d" % sampleBands[i], ylabel="band %d" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15)
        
        def colorme(x, y):
            zero = [0., 0., 0., 0., 0., 0.]
            zero[i] = x
            zero[j] = y
            return likelihood(*zero)

        colorField.map(colorme)

        plots[i,j] = Overlay(0, colorField, wakeplot, xlabel="band %d" % sampleBands[i], ylabel="band %d" % sampleBands[j], bottommargin=0.2, xlabeloffset=0.2, leftmargin=0.2, ylabeloffset=-0.15)

view(Layout(5, 5,
            None,       None,       None,       None,       plots[0,1],
            None,       None,       None,       plots[1,2], plots[0,2],
            None,       None,       plots[2,3], plots[1,3], plots[0,3],
            None,       plots[3,4], plots[2,4], plots[1,4], plots[0,4],
            plots[4,5], plots[3,5], plots[2,5], plots[1,5], plots[0,5]), width=2500, height=2500, fileName="plot_6x6grid_likelihood.svg")

#####################################################################################

def loglikelihood(p0, p1, p2, p3, p4, p5):
    return sum(numpy.square(numpy.array(numpy.matrix([[p0, p1, p2, p3, p4, p5]]) * eigenvectors).flatten()) / eigenvalues)

pictures = numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))
tmp = [loglikelihood(*projection(x)) for x in pictures]
pictures = numpy.array(map(lambda x: chi2prob.cdf(x, 5), tmp))
pictures = numpy.reshape(pictures, (images.shape[0], images.shape[1]))
onlyBand = numpy.array(numpy.power(pictures, 1) * 255., dtype=numpy.uint8)

# pictures = numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))
# pictures = numpy.array([loglikelihood(*projection(x)) for x in pictures])
# pictures = numpy.reshape(pictures, (images.shape[0], images.shape[1]))
# minvalue = numpy.percentile(pictures, 5.)
# maxvalue = numpy.percentile(pictures, 100.)
# onlyBand = numpy.array(numpy.maximum(numpy.minimum((pictures - minvalue) / (maxvalue - minvalue) * 255., 255), 0), dtype=numpy.uint8)

image = numpy.dstack((onlyBand, onlyBand, onlyBand))
image = Image.fromarray(image)
image.save("likelihood_image.png", "PNG", options="optimize")

#####################################################################################

def transformation((p0, p1, p2, p3, p4, p5)):
    return numpy.array(numpy.matrix([[p0, p1, p2, p3, p4, p5]]) * eigenvectors).flatten() / numpy.sqrt(eigenvalues)

everythingtrans = numpy.array(map(transformation, everything))
wakeloosetrans = numpy.array(map(transformation, wakeloose))
waketrans = numpy.array(map(transformation, wake))

# everything_0 = Histogram(100, -5., 25., data=everything[:,0], ymax=1000, fillcolor="lightgray")
# everything_1 = Histogram(100, -5., 5., data=everything[:,1], ymax=1000, fillcolor="lightgray")
# everything_2 = Histogram(100, -15., 5., data=everything[:,2], ymax=1000, fillcolor="lightgray")
# everything_3 = Histogram(100, -30., 10., data=everything[:,3], ymax=1000, fillcolor="lightgray")
# everything_4 = Histogram(100, -10., 3., data=everything[:,4], ymax=1000, fillcolor="lightgray")
# everything_5 = Histogram(100, -25., 5., data=everything[:,5], ymax=1000, fillcolor="lightgray")

everything_0 = Histogram(100, -50., 50., data=everythingtrans[:,0], ymax=100, fillcolor="lightgray")
everything_1 = Histogram(100, -20., 20., data=everythingtrans[:,1], ymax=100, fillcolor="lightgray")
everything_2 = Histogram(100, -20., 20., data=everythingtrans[:,2], ymax=100, fillcolor="lightgray")
everything_3 = Histogram(100, -20., 20., data=everythingtrans[:,3], ymax=100, fillcolor="lightgray")
everything_4 = Histogram(100, -1., 1., data=everythingtrans[:,4], ymax=100, fillcolor="lightgray")
everything_5 = Histogram(100, -10., 10., data=everythingtrans[:,5], ymax=100, fillcolor="lightgray")

wake_0 = Histogram(100, -50., 50., data=waketrans[:,0], fillcolor="red")
wake_1 = Histogram(100, -20., 20., data=waketrans[:,1], fillcolor="red")
wake_2 = Histogram(100, -20., 20., data=waketrans[:,2], fillcolor="red")
wake_3 = Histogram(100, -20., 20., data=waketrans[:,3], fillcolor="red")
wake_4 = Histogram(100, -1., 1., data=waketrans[:,4], fillcolor="red")
wake_5 = Histogram(100, -10., 10., data=waketrans[:,5], fillcolor="red")

wakeloose_0 = Histogram(100, -50., 50., data=wakeloosetrans[:,0], fillcolor="pink")
wakeloose_1 = Histogram(100, -20., 20., data=wakeloosetrans[:,1], fillcolor="pink")
wakeloose_2 = Histogram(100, -20., 20., data=wakeloosetrans[:,2], fillcolor="pink")
wakeloose_3 = Histogram(100, -20., 20., data=wakeloosetrans[:,3], fillcolor="pink")
wakeloose_4 = Histogram(100, -1., 1., data=wakeloosetrans[:,4], fillcolor="pink")
wakeloose_5 = Histogram(100, -10., 10., data=wakeloosetrans[:,5], fillcolor="pink")

for i, x in enumerate([everything_0, everything_1, everything_2, everything_3, everything_4, everything_5]):
    x.bottommargin = 0.15
    x.xlabeloffset = 0.15
    x.xlabel = "eigenbasis direction %d" % (i+1)

legend = Legend([[everything_0, "all pixels"], [wakeloose_0, "wake (broadly defined)"], [wake_0, "wake (strictly defined)"]], width=1, colwid=[0.2, 0.8], justify="cl")

view(Layout(2, 3,
            Overlay(0, everything_0, wakeloose_0, wake_0),
            Overlay(0, everything_1, wakeloose_1, wake_1),
            Overlay(0, everything_2, wakeloose_2, wake_2),
            Overlay(0, everything_3, wakeloose_3, wake_3),
            Overlay(0, everything_4, wakeloose_4, wake_4, legend),
            Overlay(0, everything_5, wakeloose_5, wake_5)), width=1500, height=1000, fileName="plot_naivebayes_with_pca.svg")

def loglikelihood(x):
    x = transformation(x)
    denom_loglikelihood = 0.
    numer_loglikelihood = 0.
    for i, (denomhist, numerhist) in enumerate([(everything_0, wake_0), (everything_1, wake_1), (everything_2, wake_2), (everything_3, wake_3), (everything_5, wake_5)]):
        index = denomhist.index(x[i])
        if index is None:
            denom_loglikelihood += log(1. / denomhist.entries)
            numer_loglikelihood += log(1. / numerhist.entries)
        else:
            denomvalue = denomhist.values[index] + 1e-5
            numervalue = numerhist.values[index] + 1e-5
            denom_loglikelihood += log(denomvalue / denomhist.entries)
            numer_loglikelihood += log(numervalue / numerhist.entries)
    return numer_loglikelihood / denom_loglikelihood

pictures = numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))
tmp = [loglikelihood(projection(x)) for x in pictures]
pictures = numpy.array(map(lambda x: 1. - chi2prob.cdf(x*2., 5), tmp))
pictures = numpy.reshape(pictures, (images.shape[0], images.shape[1]))
onlyBand = numpy.array(numpy.power(pictures, 1) * 255., dtype=numpy.uint8)
image = numpy.dstack((onlyBand, onlyBand, onlyBand))
image = Image.fromarray(image)
image.show()
# image.save("likelihood_naivebayes_image.png", "PNG", options="optimize")

onlyBand = numpy.array(numpy.power(pictures, 10) * 255., dtype=numpy.uint8)
image = numpy.dstack((onlyBand, onlyBand, onlyBand))
image = Image.fromarray(image)
image.show()
# image.save("likelihood_naivebayes_power10_image.png", "PNG", options="optimize")

#####################################################################################

# inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011197110KF_HYP_L1G"
# inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011210110KF_HYP_L1G"
inputDir = "/home/pivarski/NOBACKUP/KagoshimaBay/EO1H1120382011205110PF_HYP_L1G"

original_images = {}
for i, band in enumerate(sampleBands):
    original_images[band] = gdal.Open(glob.glob(inputDir + "/*_B%03d_L1T.TIF" % band)[0], gdalconst.GA_ReadOnly)
    if band < 70.5:
        original_images[band] = original_images[band].GetRasterBand(1).ReadAsArray() / 40.
    else:
        original_images[band] = original_images[band].GetRasterBand(1).ReadAsArray() / 80.

images = numpy.dstack([original_images[sampleBands[i]] for i in xrange(len(sampleBands))])
del original_images

alpha = (images[:,:,0] > 0.)
for i in xrange(1, len(sampleBands)):
    numpy.logical_and(alpha, (images[:,:,i] > 0.), alpha)

for i in xrange(len(sampleBands)):
    images[:,:,i] -= watercenter[i]

pictures = numpy.reshape(images, (images.shape[0]*images.shape[1], images.shape[2]))
alpha = numpy.reshape(alpha, (images.shape[0]*images.shape[1]))

pictures = numpy.array([(1. - chi2prob.cdf(loglikelihood(projection(x))*2., 5)) if a else 0. for x, a in zip(pictures, alpha)])

pictures = numpy.reshape(pictures, (images.shape[0], images.shape[1]))
alpha = numpy.reshape(alpha, (images.shape[0], images.shape[1]))

# onlyBand = numpy.array(pictures * 255., dtype=numpy.uint8)
# image = numpy.dstack((onlyBand, onlyBand, onlyBand, numpy.array(alpha*255, dtype=numpy.uint8)))
# image = Image.fromarray(image)
# image.show()

onlyBand = numpy.array(numpy.power(pictures, 20) * 255., dtype=numpy.uint8)
image = numpy.dstack((onlyBand, onlyBand, onlyBand, numpy.array(alpha*255, dtype=numpy.uint8)))
image = Image.fromarray(image)
# image.show()
image.save("whole_image_EO1H1120382011205110PF_HYP_L1G.png", "PNG", options="optimize")

image = numpy.dstack((onlyBand, onlyBand, numpy.zeros_like(onlyBand), onlyBand))
image = Image.fromarray(image)
# image.show()
image.save("whole_image_EO1H1120382011205110PF_HYP_L1G_translucent.png", "PNG", options="optimize")
