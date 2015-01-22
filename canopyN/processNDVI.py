# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 19:57:29 2015
This code will process NDVI for a series of HDF5 files
@author: lwasser
"""
from getFileList import geth5FileList
import h5py 
import os
os.chdir('c:/Users/lwasser/Documents/GitHub/adventures-with-python/')


dirPath = (r'c:/Users/lwasser/Documents/GitHub/adventures-with-python/data/h5/')

#get a list of all files in the directory
H5files=geth5FileList(dirPath)


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
    

def getReflectanceData(file):

    filePath =(dirPath + file)    
    

    
NDVIdict={}   

for file in H5files:
    filePath =(dirPath + file) 
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the flightline 
    reflectance=H5file['/Reflectance']
    
    ndviOut=processNDVI(reflectance)
    #get plot name
    if file.endswith('.h5'):
      plot = file[:-3]
    print plot
    NDVIdict[plot]=ndviOut
    H5file.close()
    

