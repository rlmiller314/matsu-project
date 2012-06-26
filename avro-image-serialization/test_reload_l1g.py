import json

import numpy
from PIL import Image

import GeoPictureSerializer
geoPicture = GeoPictureSerializer.deserialize(open("/mnt/tmp2.txt"))

print json.loads(geoPicture.metadata["L1T"])
print geoPicture.bands
print geoPicture.picture.shape
print geoPicture.picture

# just pull out red, green, blue
geoPicture.picture = geoPicture.picture[:,:,(geoPicture.bands.index("B029"), geoPicture.bands.index("B023"), geoPicture.bands.index("B016"))]

image = Image.fromarray(numpy.array(geoPicture.picture, dtype=numpy.uint8))
image.save("/var/www/quick-look/tmp2.png", "PNG", option="optimize")
