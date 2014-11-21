# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 16:03:02 2014

@author: lwasser
"""
#http://stackoverflow.com/questions/6046038/open-file-on-separate-drive-in-python

import os
import sys

#path = sys.argv[1]
#path = 'F:\D17_Data_2014_Distro\02_SJER\SJER_Spectrometer_Data\2013061320\Reflectance\NIS1_20130613_134931_atmcor.h5'
path = (r'F:\D17_Data_2014_Distro\02_SJER\NIS1_20130613_134931_atmcor.h5')
#path='F:\TestChip\hdf5_Test'
basepath, fname = os.path.split(path)
print "directory:", basepath
if os.path.exists(basepath):
    print "directory exists"
else:
    print "directory does not exist!"
    sys.exit()

if not fname:
    print "no filename provided!"
    sys.exit()
print "filename:", fname
if os.path.exists(path):
    print "filename exists"
else:
    print "filename not found!"
    print "directory contents:"
    for fn in os.listdir(basepath):
        print fn