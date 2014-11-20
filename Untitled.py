# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 18:40:32 2014

@author: law
"""

import h5py
import numpy
f = h5py.File('new.h5', 'w')
dset= f['dset']

#f['dset'] = numpy.zeros((6,4), dtype=numpy.int32)

dset.attrs['Units'] = [100, 200]
f.close()