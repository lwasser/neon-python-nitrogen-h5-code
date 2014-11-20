# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 18:40:32 2014

@author: law
"""

import h5py
import numpy
f = h5py.File('new.h5', 'a')
dset= f['new']
#grp = f.create_group("bar")
#f['dset'] = numpy.zeros((6,4), dtype=numpy.int32)
#file.visititems(lambda name, object: print(name))
#dset.attrs['Units'] = [100, 200]
f.close()