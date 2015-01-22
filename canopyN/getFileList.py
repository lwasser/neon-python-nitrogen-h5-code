# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 20:02:13 2015

@author: lwasser
"""

def geth5FileList(fileDirectory):
    '''
    This function returns a list of hdf5 files in a given directory.
    inputs: fileDirectory - path to files
    output onlyH5Files - a list of file names
    '''
    from os import listdir
    from os.path import isfile, join
    
    onlyfiles = [ f for f in listdir(fileDirectory) if isfile(join(fileDirectory,f)) ]

    #Generate a list of the names of H5 files in the specified directory
    onlyH5files=[]
    for f in onlyfiles:
      if f.endswith(".h5"):
        onlyH5files.append(f)
        
    return onlyH5files    