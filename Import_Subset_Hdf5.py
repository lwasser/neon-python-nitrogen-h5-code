# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 16:55:56 2014

@author: lwasser
"""
#%%
import h5py 
#open the hdf5 file
#hdf5_file_name = '/Users/lwasser/Documents/Conferences/1_DataWorkshop_ESA2014/HDF5File/SJER_140123_chip.h5'

#the "r" is important as it tells python to read in the characters without converting them.
#filePath = (r'F:\D17_Data_2014_Distro\02_SJER\SJER_Spectrometer_Data\2013061320\Reflectance\NIS1_20130613_134931_atmcor.h5')
filePath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/NIS1_20130613_134931_atmcor.h5')

file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode

#Select the reflectance dataset    
reflectance=file['/Reflectance']
    
#subset out reflectance
plotReflectance=reflectance[50:60,3000:4000,300:600]   
print "Reflectance cropped"
#%%
#https://confluence.slac.stanford.edu/display/PSDM/How+to+access+HDF5+data+from+Python#HowtoaccessHDF5datafromPython-HDF5filestructure

#create SJER Plot Data 
#remember that the slashes are backwards in windows...
plots = h5py.File('data/SJERPlots.h5', 'a')   #a is read / write  
#assign the reflectance values to a group

del plots['plotOne']
plots['plotOne'] = plotReflectance

file.close()
plots.close()

print "That's All Folks!"
#%%
# if you want to delete a group 
#this loops through the file metadata and prints out attributes for each item (which happens to be the wavelengths)
#for item in file.attrs.keys():
#    print item + ":", file.attrs[item]
    
#    file.keys() 
#    file.values()