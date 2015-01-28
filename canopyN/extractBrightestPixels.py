# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 16:42:28 2015

@author: lwasser
"""

import numpy as np

def findBrightPixels(spectra,NDVIBool): 
    '''
    This function finds the brightest pixels based upon a defined NDVI threshold
    Inputs: hyperspectral dataset, 
    NDVI boolean where true = values > NDVI threshold
    Outputs: an array of the spectra for the areas of NDVI brightest values
    '''
    fnBrightPixels=[]
    for band in range(len(spectra)):   
        tmpBrightPixels=[]
        #extra a bands worth of data
        data=spectra[band]
        #select pixels in the band where NDVI > threshold
        tmpBrightPixels = data[NDVIBool]
        fnBrightPixels.append(tmpBrightPixels)
        #print band
    return np.array(fnBrightPixels)
           
           
#reflectance,brightestBool  
# brightPixels=findBrightPixels(reflectance,brightestBool)    

#filePath =(plotH5FilePath + file) 
#open the h5 file     
#H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
#Select the reflectance dataset within the flightline 
#reflectance=H5file['/Reflectance']


#for band in range(len(reflectance)):   
    #tmpBrightPixels=[]
    #extra a bands worth of data
#    data=reflectance[band]
    #select pixels in the band where NDVI > threshold
#    tmpBrightPixels = data[brightestBool]
#    fnBrightPixels.append(tmpBrightPixels)
#    del tmpBrightPixels
        