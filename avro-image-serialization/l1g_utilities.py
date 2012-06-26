import datetime
import time
import json

import numpy
from PIL import Image
from osgeo import osr

import GeoPictureSerializer

osr.UseExceptions()

class L1GPicture:
    def __init__(self, inputStream):
        "Load a picture from a serialized stream (pass a file-like object or a serialized string, but not a fileName).  Takes 30 seconds."
        self._geoPicture = GeoPictureSerializer.deserialize(inputStream)

    def bands(self):
        "Return a list of all bands in this picture."
        return self._geoPicture.bands

    def array(self, bandNames=None):
        "Return a NumPy array of the picture, optionally selecting a set of bandNames (tuple of strings)."
        if bandNames is None:
            return self._geoPicture.picture
        else:
            return self._geoPicture.picture[:,:,[self._geoPicture.bands.index(b) for b in bandNames]]

    def mask(self, bandNames=None):
        "Return a boolean-valued NumPy mask array for non-zero entries in a given set of bandNames (tuple of strings)."

        if bandNames is None:
            bandNames = self.bands()

        alphaBand = (self._geoPicture.picture[:,:,self._geoPicture.bands.index(bandNames[0])] > 0)
        for band in bandNames[1:]:
            numpy.logical_and(alphaBand, (self._geoPicture.picture[:,:,self._geoPicture.bands.index(band)] > 0), alphaBand)
        return alphaBand

    def corners(self, bandNames=None):
        "Return the corners of the tilted rectangle of valid image data as (x, y) pixel coordinates."
        alpha = self.mask(bandNames)
        alphaT = numpy.transpose(alpha)
        ysize, xsize = alpha.shape

        output = []
        for i in xrange(ysize):
            if numpy.count_nonzero(alpha[i]) > 0:
                break
        output.append((numpy.argwhere(alpha[i]).mean(), i))

        for i in xrange(xsize):
            if numpy.count_nonzero(alphaT[i]) > 0:
                break
        output.append((i, numpy.argwhere(alphaT[i]).mean()))

        for i in xrange(ysize - 1, 0, -1):
            if numpy.count_nonzero(alpha[i]) > 0:
                break
        output.append((numpy.argwhere(alpha[i]).mean(), i))

        for i in xrange(xsize - 1, 0, -1):
            if numpy.count_nonzero(alphaT[i]) > 0:
                break
        output.append((i, numpy.argwhere(alphaT[i]).mean()))

        return output

    def png(self, redBand, greenBand, blueBand, minRadiance=None, maxRadiance=None, fileName="/var/www/quick-look/tmp.png", alpha=True):
        "Turn three bands into an RGB(A) PNG picture for quick viewing."

        if minRadiance is None:
            minRadiance = min(self._geoPicture.picture[:,:,self._geoPicture.bands.index(redBand)].min(),
                              self._geoPicture.picture[:,:,self._geoPicture.bands.index(greenBand)].min(),
                              self._geoPicture.picture[:,:,self._geoPicture.bands.index(blueBand)].min())
        if maxRadiance is None:
            maxRadiance = max(self._geoPicture.picture[:,:,self._geoPicture.bands.index(redBand)].max(),
                              self._geoPicture.picture[:,:,self._geoPicture.bands.index(greenBand)].max(),
                              self._geoPicture.picture[:,:,self._geoPicture.bands.index(blueBand)].max())

        picture = (self._geoPicture.picture[:,:,(self._geoPicture.bands.index(redBand),
                                                 self._geoPicture.bands.index(greenBand),
                                                 self._geoPicture.bands.index(blueBand))] - minRadiance) * 255./(maxRadiance - minRadiance)
        numpy.maximum(picture, 0., picture)
        numpy.minimum(picture, 255., picture)
        picture = numpy.array(picture, dtype=numpy.uint8)

        if alpha:
            alphaBand = numpy.array(self.mask((redBand, greenBand, blueBand)), dtype=numpy.uint8) * 255
            image = Image.fromarray(numpy.dstack((picture[:,:,0], picture[:,:,1], picture[:,:,2], alphaBand)))
            image.save(fileName, "PNG", option="optimize")
        else:
            image = Image.fromarray(picture)
            image.save(fileName, "PNG", option="optimize")

    def wavelength(self, bandName):
        "Given a band name like 'B040', return a wavelength in nanometers."

        bandNumber = int(bandName[1:])
        if bandNumber < 70.5:
            return (bandNumber - 10.) * 10.213 + 446.
        else:
            return (bandNumber - 79.) * 10.110 + 930.

    def longLat(self, x, y):
        "Convert an (x, y) pixel position into a (longitude, latitude) pair.  Note that the array is indexed as array[y,x] and coordinates passed to this function need not be integers."

        spatialReference = osr.SpatialReference()
        spatialReference.ImportFromWkt(self._geoPicture.metadata["Projection"])
        coordinateTransform = osr.CoordinateTransformation(spatialReference, spatialReference.CloneGeogCS())
        tlx, weres, werot, tly, nsrot, nsres = json.loads(self._geoPicture.metadata["GeoTransform"])
        longitude, latitude, altitude = coordinateTransform.TransformPoint(tlx + weres * x, tly + nsres * y)
        return longitude, latitude

    def L1T(self):
        "Return all of the metadata from the original .L1T file as a dictionary of dictionaries."
        return json.loads(self._geoPicture.metadata["L1T"])

    def acquisitionTime(self, numeric=False):
        "Return the picture acquisition (start_time, stop_time) as Python datetime objects or as numeric timestamps."
        l1t = self.L1T()
        start_time = datetime.datetime.strptime(l1t["PRODUCT_METADATA"]["START_TIME"], "%Y %j %H:%M:%S")
        end_time   = datetime.datetime.strptime(l1t["PRODUCT_METADATA"]["END_TIME"], "%Y %j %H:%M:%S")
        if numeric:
            return time.mktime(start_time.timetuple()), time.mktime(end_time.timetuple())
        else:
            return start_time, end_time

    def lookAngle(self):
        "Return the satellite's look angle (convenience function for float(self.L1T()[\"PRODUCT_PARAMETERS\"][\"SENSOR_LOOK_ANGLE\"]))."
        return float(self.L1T()["PRODUCT_PARAMETERS"]["SENSOR_LOOK_ANGLE"])

    def sunAngle(self):
        "Return the sun's azimuth and elevation angle (convenience function for float(self.L1T()[\"PRODUCT_PARAMETERS\"][\"SUN_AZIMUTH\"]) and [\"SUN_ELEVATION\"])."
        l1t = self.L1T()
        return float(l1t["PRODUCT_PARAMETERS"]["SUN_AZIMUTH"]), float(l1t["PRODUCT_PARAMETERS"]["SUN_ELEVATION"])




p = L1GPicture(open("/mnt/pictures-L1G-serialized/EO1H1430472010084110PF_HYP_L1G.serialized"))
p.png("B029", "B023", "B016")
print p.corners(("B029", "B023", "B016"))
print [p.longLat(x, y) for x, y in p.corners(("B029", "B023", "B016"))]
