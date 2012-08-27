#!/usr/bin/env python

import os
import sys
import getopt
from distutils.core import setup, Extension
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import numpy

config = configparser.ConfigParser()
config.read("../../../CONFIG.ini")

AVRO_HOME = config.get("DEFAULT", "env.AVRO_HOME")
BOOST_INCLUDEDIR = config.get("DEFAULT", "env.BOOST_INCLUDEDIR")
BOOST_LIBRARYDIR = config.get("DEFAULT", "env.BOOST_LIBRARYDIR")

print AVRO_HOME

otherargs = []
for arg in sys.argv:
    if arg.find("with-avro") != -1 or arg.find("with-boostinclude") != -1 or arg.find("with-boostlib") != -1:
        optlist, argv = getopt.getopt([arg], "", ["with-avro=", "with-boostinclude=", "with-boostlib="])
        for name, value in optlist:
            if name == "--with-avro":
                AVRO_HOME = value
            if name == "--with-boostinclude":
                BOOST_INCLUDEDIR = value
            if name == "--with-boostlib":
                BOOST_LIBRARYDIR = value
    else:
        otherargs.append(arg)
sys.argv = otherargs

AVRO_INCLUDE = os.path.join(AVRO_HOME, "include")
AVRO_LIB = os.path.join(AVRO_HOME, "lib")

print("************************************************************************************************")
print("Assuming AVRO includes and libraries are in %s and %s" % (AVRO_INCLUDE, AVRO_LIB))
print("************************************************************************************************")

print("************************************************************************************************")
print("Assuming Boost includes and libraries are in %s and %s" % (BOOST_INCLUDEDIR, BOOST_LIBRARYDIR))
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
                             library_dirs=[AVRO_LIB, BOOST_LIBRARYDIR],
                             libraries=["avrocpp"],
                             include_dirs=[AVRO_INCLUDE, BOOST_INCLUDEDIR, numpy.get_include()],
                             )])
