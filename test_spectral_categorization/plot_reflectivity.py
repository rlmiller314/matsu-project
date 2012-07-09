import json
import math

from cassius import *

scan_results = json.load(open("scan_results.json"))

radiance = []
sun_elevation = []
sun_azimuth = []
look_angle = []
for picture in scan_results["data"]:
    if picture["sampleband"] == 25:
        radiance.append(float(picture["radiance"]))
        sun_elevation.append(float(picture["L1T"]["PRODUCT_PARAMETERS"]["SUN_ELEVATION"]))
        sun_azimuth.append(float(picture["L1T"]["PRODUCT_PARAMETERS"]["SUN_AZIMUTH"]))
        look_angle.append(float(picture["L1T"]["PRODUCT_PARAMETERS"]["SENSOR_LOOK_ANGLE"]))

linear = Curve("450*x*pi/180.", 0, 90, linecolor="blue", linestyle="dashed")
sine = Curve("450*sin(x*pi/180.)", 0, 90, linecolor="red", linestyle="dashed")
elevation = Scatter(x=sun_elevation, y=radiance, markersize=0.25)
legend = Legend([[elevation, "band 25, all pictures"], [sine, "450 sin(elevation angle)"], [linear, u"450 (\u03c0/180) elevation angle"]], anchor="tl", x=0, justify="cl", colwid=[0.2, 0.8], width=0.6)
view(Overlay(linear, sine, elevation, legend, xmin=-70, xmax=70, ymin=-100, ymax=600, xlabel="elevation angle [degrees]", ylabel=u"average radiance [W/m/m/sr/\u03bcm]"))


linear = Curve("500.*x", 0., 1., linecolor="blue", linestyle="dashed")
elevation = Scatter(x=[math.sin(x*math.pi/180.) for x in sun_elevation], y=radiance, markersize=0.25)
legend = Legend([[elevation, "band 25, all pictures"], [linear, u"500 sin(elevation)"]], anchor="tl", x=0, justify="cl", colwid=[0.2, 0.8], width=0.5)
view(Overlay(linear, elevation, legend, xmin=-1., xmax=1., ymin=-100, ymax=600, xlabel="sin(elevation angle)", ylabel=u"average pixel radiance [W/m/m/sr/\u03bcm]"), fileName="reflectivity.svg")


# view(Scatter(x=look_angle, y=[y/(500.*math.sin(x*math.pi/180.)) for x, y in zip(sun_elevation, radiance)], markersize=0.25, ymin=0., ymax=1.))

# view(Scatter(x=[math.sin(x*math.pi/180.) for x in sun_elevation], y=radiance, markersize=0.25))
