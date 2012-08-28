from math import floor
import struct
import random
random.seed(12345)

import jpype

def tileIndex(depth, longitude, latitude):  
    "Inputs a depth and floating-point longitude and latitude, outputs a triple of index integers."
    if abs(latitude) > 90.: raise ValueError("Latitude cannot be %s" % str(latitude))
    longitude += 180.
    latitude += 90.
    while longitude <= 0.: longitude += 360.
    while longitude > 360.: longitude -= 360.
    longitude = int(floor(longitude/360. * 2**(depth+1)))
    latitude = min(int(floor(latitude/180. * 2**(depth+1))), 2**(depth+1) - 1)
    return depth, longitude, latitude

def tileName(depth, longIndex, latIndex):
    "Inputs an index-triple, outputs a string-valued name for the index."
    return "T%02d-%05d-%05d" % (depth, longIndex, latIndex)  # constant length up to depth 15

def fixedWidthHex(number):
    "Represents an 8-byte signed number as a fixed-width hexidecimal string without a minus sign."
    return "%016x" % struct.unpack("Q", struct.pack("q", hash(number)))[0]

timestamp = random.randint(1000000000, 9999999999)   # I'm simulating one image, so there's only one timestamp

classpath = "matsuAccumuloInterface.jar"
jpype.startJVM("/usr/lib/jvm/java-6-sun/jre/lib/amd64/server/libjvm.so", "-Djava.class.path=%s" % classpath)
AccumuloInterface = jpype.JClass("org.occ.matsu.AccumuloInterface")

AccumuloInterface.connectForWriting("accumulo", "192.168.18.101:2181", "root", "password", "MatsuLevel2LngLat")

for i in xrange(100):
    longitude, latitude = random.gauss(94.312, 0.1), random.gauss(40.183, 0.1)
    identifier = hash((int(round(100.*longitude)), int(round(100.*latitude))))

    key = "%s-%010d-%s" % (tileName(*tileIndex(10, longitude, latitude)), timestamp, fixedWidthHex(identifier))

    print key, longitude, latitude
    AccumuloInterface.lnglat_write(key, longitude, latitude, "{}")

AccumuloInterface.finishedWriting()

jpype.shutdownJVM()
