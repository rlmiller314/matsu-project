#!/bin/env sh

################################################################################
#
#   Environment variables for the user to set
#
#   This is where the image libraries will be installed.
#   To uninstall, just remove this directory.
export IMAGELIBRARY_DIRECTORY=/opt/imagelibraries
#
#   This is where the packages will be downloaded and compiled.
#   You can delete this after installation and everything should still work.
export PACKAGE_CACHE_DIRECTORY=/tmp/package_cache
#
#   This is a script that you should source ("source setup_environment.sh")
#   after each login to use the compiled Python and libraries, rather than
#   the default ones.  (Note: "./setup_environment.sh" is not sufficient.)
export SETUP_ENVIRONMENT=setup_environment.sh
#
################################################################################
#
#   This script replaces the contents of $IMAGELIBRARY_DIRECTORY,
#   $PACKAGE_CACHE_DIRECTORY, and $SETUP_ENVIRONMENT with a new copy
#   downloaded and compiled from the Internet.
#
#   To use (after possibly changing the three environment variables above):
#
#       ./download_and_compile.sh
#       (wait half an hour)
#
#       source setup_environment.sh
#       (new software is ready to use)
#
################################################################################

# 0. Create a directory in which to install everything

cat > $SETUP_ENVIRONMENT <<EOF

export PYTHONPATH=$IMAGELIBRARY_DIRECTORY/lib/python:$PYTHONPATH
export LD_LIBRARY_PATH=$IMAGELIBRARY_DIRECTORY/lib:$LD_LIBRARY_PATH
export PATH=$IMAGELIBRARY_DIRECTORY/bin:$PATH

EOF

chmod 755 setup_environment.sh
source setup_environment.sh

rm -rf $IMAGELIBRARY_DIRECTORY
rm -rf $PACKAGE_CACHE_DIRECTORY

mkdir $IMAGELIBRARY_DIRECTORY
mkdir $PACKAGE_CACHE_DIRECTORY
cd $PACKAGE_CACHE_DIRECTORY

# 1. Install most prerequisites from packages

yum -y install unzip.x86_64
yum -y install make.x86_64

yum -y install gcc.x86_64                 # everything needs a C compiler
yum -y install gcc-gfortran.x86_64        # SciPy *might* be the only one that needs Fortran and C++
yum -y install gcc-c++.x86_64

yum -y install blas-devel.x86_64          # linear algebra for SciPy
yum -y install lapack-devel.x86_64

yum -y install zlib-devel.x86_64          # for PIL's PNG support

# 2. Install Python 2.7.3 (there wasn't any particular reason for 2.7 rather than 2.6)

wget http://python.org/ftp/python/2.7.3/Python-2.7.3.tgz
tar -xzvf Python-2.7.3.tgz
cd Python-2.7.3
./configure --prefix=$IMAGELIBRARY_DIRECTORY
make
make install
cd ..

# 3. Install NumPy 1.6.2

wget 'http://downloads.sourceforge.net/project/numpy/NumPy/1.6.2/numpy-1.6.2.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fnumpy%2Ffiles%2FNumPy%2F1.6.2%2F&ts=1339612771&use_mirror=voxel'
tar -xzvf numpy-1.6.2.tar.gz
cd numpy-1.6.2
python setup.py install --home=$IMAGELIBRARY_DIRECTORY
cd ..

# 4. Install SciPy 0.10.1

wget 'http://downloads.sourceforge.net/project/scipy/scipy/0.10.1/scipy-0.10.1.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fscipy%2Ffiles%2Fscipy%2F0.10.1%2F&ts=1339612599&use_mirror=hivelocity'
tar -xzvf scipy-0.10.1.tar.gz
cd scipy-0.10.1
python setup.py install --home=$IMAGELIBRARY_DIRECTORY
cd ..

# 5. Install PIL 1.1.7

wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
tar -xzvf Imaging-1.1.7.tar.gz
cd Imaging-1.1.7
sed 's/^ZLIB_ROOT = None$/ZLIB_ROOT = "\/usr\/lib64", "\/usr\/include"/' < setup.py > /tmp/TMP
cp -f /tmp/TMP setup.py
python setup.py install --home=$IMAGELIBRARY_DIRECTORY
cd ..

# 6. Install PROJ.4 from source

wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
tar -xzvf proj-4.8.0.tar.gz
cd proj-4.8.0
./configure --prefix=$IMAGELIBRARY_DIRECTORY
make
make install
cd ..

# 7. Install GDAL with its Python bindings

wget http://download.osgeo.org/gdal/gdal191.zip
unzip gdal191.zip
cd gdal-1.9.1/
./configure --prefix=$IMAGELIBRARY_DIRECTORY --with-python
make
make install
cd swig/python
python setup.py install --home=$IMAGELIBRARY_DIRECTORY
cd ../../..

################################################################################
#
#   Second part: Avro serialization
#
################################################################################

# 1. Install most prerequisites from packages

yum -y install cmake
yum -y install boost141-devel.x86_64 boost141-filesystem.x86_64 boost141-system.x86_64 boost141-program-options.x86_64 

export BOOST_INCLUDEDIR=/usr/include/boost141
export BOOST_LIBRARYDIR=/usr/lib64/boost141

# 2. Install Avro

wget http://mirrors.sonic.net/apache/avro/avro-1.7.1/cpp/avro-cpp-1.7.1.tar.gz
tar -xzvf avro-cpp-1.7.1.tar.gz
cd avro-cpp-1.7.1
cmake -G "Unix Makefiles"
make
make package
tar -xzvf avrocpp-1.7.1.tar.gz
cp -a avrocpp-1.7.1/include/avro/ $IMAGELIBRARY_DIRECTORY/include/
cp -a avrocpp-1.7.1/lib/libavrocpp* $IMAGELIBRARY_DIRECTORY/lib/
cp -a avrocpp-1.7.1/bin/avrogencpp $IMAGELIBRARY_DIRECTORY/bin/
cd ..

# 3. Get the whole matsu-project to install the serialization engine

wget --no-check-certificate https://github.com/opencloudconsortium/matsu-project/tarball/master -O matsu-project.tar.gz
tar -xzvf matsu-project.tar.gz
cd opencloudconsortium-matsu-project-*
cd Libraries/Serialization\ with\ Avro/
python setup.py install --home=$IMAGELIBRARY_DIRECTORY --with-avro=$IMAGELIBRARY_DIRECTORY
cd ../../..

