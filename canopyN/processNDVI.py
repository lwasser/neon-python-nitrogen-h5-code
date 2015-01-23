# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 19:57:29 2015
This code will process NDVI for a series of HDF5 files
@author: lwasser
"""
from getFileList import geth5FileList
import h5py 
import os
from writeGeotiff import writeGeotiff
os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/')


dirPath = (r'c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/h5/')

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
    
#def getReflectanceData(file):
#    filePath =(dirPath + file)    
    
from extractBrightestPixels import findBrightPixels

#########################
# clean out directory of tifs
#########################

#from cleanOutDir import cleanOutDir
#first clear out the H5 directory
#cleanOutDir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/NDVItiff/*.tif')

NDVIdict={}   
brightPixels=[]
for file in H5files:
    brightPixels=[]
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
    #write the NDVI out as a geotif!
    filename=('NDVItiff/' + plot + '.tif' )
    writeGeotiff(filename,ndviOut,plotBound[plot][0],plotBound[plot][3])
    #create dictionary of NDVI values for kicks
    NDVIdict[plot]=ndviOut
    brightestBool=ndviOut>.5
    #lastly, extract brightest pixels
    brightPixels=findBrightPixels(reflectance,brightestBool)
    
    #create H5 output
    #create empty H5 File - this is where all of the plot data will be stored
    hFile = h5py.File('data/brightPixelsH5/' + plot + '.h5', 'a')  
    #grp = hFile.create_group("Reflectance")
    hFile['Reflectance'] = plotReflectance
    file.close()
    hFile.close()
    
    #close all files
    H5file.close()
    
################################
#calculate stuff using only the brightest pixels
#under development!!
################################
for file in H5files:
    filePath =(dirPath + file) 
    if file.endswith('.h5'):
      plot = file[:-3]
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode

    brightPixels= NDVIdict[plot] >.5 
    
    #close the file    
    H5file.close()

