# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 19:57:29 2015
This code will process NDVI for a series of HDF5 files
@author: lwasser
"""

import numpy as np

#os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/')


#dirPath = (r'c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/h5/')

#get a list of all files in the directory
#H5files=geth5FileList(dirPath)

#Tried to get close to landsat 8 bands in the averages for NDVI
#Landsat 8 Red Band: .64-67
#NIS red bands: 54-57
#b54:647.76
#b55:652.77
#b56:657.78
#b57:662.79


#Landsat RED: 850-880nm
#bands 96-99 
#b96: 858.16
#b97: 863.17
#b98: 868.18
#b99: 873.18

#remember that python has 0 based indexing so the band number is actually
#band number - 1 (ie band 1 - an index value of 0)
def processNDVI(spectra,redBand=53,NIRband=95, redEnd=57, NIRend=99):
    '''This function will run NDVI on spectra
    inputs: spectra (numpy array)
    redBand start: 53
    NIRband start: 95
    redEnd: 57
    NIRend: 99
    optional inputs (the starting and ending location for the red and NIR bands)
    outputs NDVI matrix. It will average bands closest to NIS bands
    '''
    
    #when you select in python, the second number is -1. 
    red=np.mean(spectra[redBand:(redEnd+1),:,:],axis=0)
    NIR=np.mean(spectra[NIRband:(NIRend+1),:,:],axis=0)
        
    #NIR=(spectra[NIRband,:,:]).astype('float')
    #code when not averaging bands    
    #NIR=(spectra[NIRband,:,:]).astype('float')
    #red=(spectra[redBand,:,:]).astype('float')

    NDVI=(NIR-red)/ (NIR+red)
    return NDVI
