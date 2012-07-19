#!/bin/env sh

# 0. Create a directory in which to install everything

export IMAGELIBRARY_DIRECTORY=/opt/imagelibraries

cat > setup_environment.sh <<EOF

export PYTHONPATH=$IMAGELIBRARY_DIRECTORY/lib/python:$PYTHONPATH
export LD_LIBRARY_PATH=$IMAGELIBRARY_DIRECTORY/lib:$LD_LIBRARY_PATH
export PATH=$IMAGELIBRARY_DIRECTORY/bin:$PATH

EOF

chmod 755 setup_environment.sh
source setup_environment.sh

export PACKAGE_CACHE_DIRECTORY=/tmp/package_cache

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
