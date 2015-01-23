# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 16:42:28 2015

@author: lwasser
"""

def findBrightPixels(spectra,NDVIBool): 
    '''
    This function finds the brightest pixels based upon a defined NDVI threshold
    Inputs: hyperspectral dataset, 
    NDVI boolean where true = values > NDVI threshold
    Outputs: an array of the spectra for the areas of NDVI brightest values
    '''
    brightPixels=[]
    for band in range(len(spectra)):   
        tmpBrightPixels=[]
        #extra a bands worth of data
        data=spectra[band]
        #select pixels in the band where NDVI > threshold
        tmpBrightPixels = data[NDVIBool]
        brightPixels.append=tmpBrightPixels
        
    return brightPixels
        