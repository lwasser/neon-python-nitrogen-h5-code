# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 19:57:29 2015
This code will process NDVI for a series of HDF5 files
@author: lwasser
"""
from getFileList import geth5FileList
import h5py 
import os
#os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/')


#dirPath = (r'c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/h5/')

#get a list of all files in the directory
#H5files=geth5FileList(dirPath)


def processNDVI(spectra,redBand=52,NIRband=96):
    '''This function will run NDVI on spectra
    inputs: spectra (numpy array)
    optional inputs (red and NIR bands)
    outputs NDVI matrix
    '''
    
    NIR=(spectra[NIRband,:,:]).astype('float')
    red=(spectra[redBand,:,:]).astype('float')
    
    NDVI=(NIR-red)/ (NIR+red)
    return NDVI
