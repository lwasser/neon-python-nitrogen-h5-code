# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 11:12:40 2014
This code will loop through all HDF5 files in a directory and grab the extents, map info and rotation creating a 
matrix of values to search on.
@author: law
"""

#import libraries that Python needs to read shapefiles
import h5py 
import numpy as np

#enter the directory that you wish to explore
fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')

#get a list of all files in the directory
from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir(fileDirectory) if isfile(join(fileDirectory,f)) ]

#just pull out the files that are h5 files (ignore other extensions)
onlyH5files=[]
for f in onlyfiles:
  if f.endswith(".h5"):
    onlyH5files.append(f)
    
#should be able to populate this ahead of time with Nan
finalLookup=[]   
#for f in onlyH5files:
    #iterate through all H5 files in the directory
for f in xrange(len(onlyH5files)):
    print(f)
    #open the file name to the directory path so the code knows where to find
    #the hdf5 file to open.
    filePath=join(fileDirectory,onlyH5files[f])
    #open hdf5 file  
    file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the H5 file and associated needed attributes. 
    reflectance=file['/Reflectance']
    CRS=file['/coordinate system string']
    mapInfo=['/map info']
    
    #Split map info string to extract raster corner location
    mapInfo=str(file['map info'][:]).split(',')
    eastingUL=float(mapInfo[3])
    northingUL=float(mapInfo[4])
    xsize=float(mapInfo[5])
    ysize=float(mapInfo[6])
    zone=int(mapInfo[7])
    
    #grab the shape of the reflectance matrix (the raster size) 
    #Use this to define raster x,y,z extent (matrix dimensions)
    nb,nY,nX=reflectance.shape
    
    #find the extents of the hdf5 file
    yTop=northingUL
    yBot=northingUL-nY*ysize
    xLeft=eastingUL
    xRight=eastingUL+nX*xsize
    
    #be sure to close the file
    file.close() 

    #write out elements into a list
    fileExtents=[onlyH5files[f],yTop,yBot,xLeft,xRight,mapInfo]  
    finalLookup.append(fileExtents)

#%reset clears all variables
print("all done!")