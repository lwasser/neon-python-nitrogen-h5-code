# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 15:35:00 2014
# this code will extract metatdata from the NIS h5 files in order 
to figure out which plots are in which flight lines
@author: law
"""

#load needed packages
import h5py 
# numpy for math calcs
import numpy as np

#Read in File - remember paths are different mac vs pc
#filePath = (r'F:\D17_Data_2014_Distro\02_SJER\SJER_Spectrometer_Data\2013061320\Reflectance\NIS1_20130613_134931_atmcor.h5')
filePath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/NIS1_20130613_141829_atmcor.h5')

file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode


#Select the reflectance dataset and the attributes we will need. 
   
reflectance=file['/Reflectance']
CRS=file['/coordinate system string']
mapInfo=['/map info']

#by splitting the map info string i can figure out the bounding start location
# for the raster
mapInfo=str(file['map info'][:]).split(',')
eastingUL=float(mapInfo[3])
northingUL=float(mapInfo[4])
xsize=float(mapInfo[5])
ysize=float(mapInfo[6])
zone=int(mapInfo[7])
#grab the shape of the file and use that to define the dataset extent
#nb,nY,nX=np.shape(file['Reflectance'][:,:,:]) <-too slow!
nb,nY,nX=reflectance.shape

#find the extents of the hdf5 file
yTop=northingUL
yBot=northingUL-nY*ysize
xLeft=eastingUL
xRight=eastingUL+nX*xsize


f.close()


