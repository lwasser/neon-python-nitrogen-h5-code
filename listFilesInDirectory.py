# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 10:53:36 2014
This codes explores a specified directory and extracts a list of all file contents in the directory. 
@author: Leah A. Wasser
"""

# http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
#this code will extract a list of files from a directory


#enter the directory that you wish to explore
mypath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')

#get a list of all files in the directory
from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

#just pull out the files that are h5 files (ignore other extensions)
onlyfiles1=[]
for f in onlyfiles:
  if f.endswith(".h5"):
    onlyfiles1.append(f)
    
#Type in onlyfiles1[0] for example to call the first file in the directory
onlyfiles1[0]
