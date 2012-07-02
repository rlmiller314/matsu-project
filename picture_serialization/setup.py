#!/usr/bin/env python

import os
import sys
import getopt
from distutils.core import setup, Extension
import numpy

AVRO_HOME = "/usr"

otherargs = []
for arg in sys.argv:
    if arg.find("with-avro") != -1:
        optlist, argv = getopt.getopt([arg], "", ["with-avro="])
        for name, value in optlist:
            if name == "--with-avro":
                AVRO_HOME = value
    else:
        otherargs.append(arg)
sys.argv = otherargs

AVRO_INCLUDE = os.path.join(AVRO_HOME, "include")
AVRO_LIB = os.path.join(AVRO_HOME, "lib")

print("************************************************************************************************")
print("Assuming AVRO includes and libraries are in %s and %s" % (AVRO_INCLUDE, AVRO_LIB))
print("************************************************************************************************")

setup(name="GeoPictureSerializer",
      version="0.1.0",
      description="Module to serialize geo-tagged images and their metadata with Avro",
      author="Jim Pivarski",
      author_email="jim.pivarski@opendatagroup.com",
      url="http://www.opendatagroup.com",
      package_dir={"": "lib"},
      ext_modules=[Extension("GeoPictureSerializer",
                             [os.path.join("GeoPictureSerializer.cpp")],
                             library_dirs=[AVRO_LIB],
                             libraries=["avrocpp"],
                             include_dirs=[AVRO_INCLUDE, numpy.get_include()],
                             )])
