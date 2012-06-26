import sys
import json
import time

import numpy
from PIL import Image

import GeoPictureSerializer

inputFileName = sys.argv[1]
print "loading", inputFileName

tmp = time.time()
geoPicture = GeoPictureSerializer.deserialize(open(inputFileName))
print "time to load:", time.time() - tmp

# just pull out red, green, blue
maxRadiance = max(geoPicture.picture[:,:,geoPicture.bands.index("B029")].max(),
                  geoPicture.picture[:,:,geoPicture.bands.index("B023")].max(),
                  geoPicture.picture[:,:,geoPicture.bands.index("B016")].max())

picture = geoPicture.picture[:,:,(geoPicture.bands.index("B029"), geoPicture.bands.index("B023"), geoPicture.bands.index("B016"))] * 255./maxRadiance

image = Image.fromarray(numpy.array(picture, dtype=numpy.uint8))
image.save("/var/www/quick-look/tmp2.png", "PNG", option="optimize")

print "done: load the webpage!"
