# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 16:44:43 2015

@author: lwasser
"""
def cleanOutDir(path):
    '''
    This function will remove all files from a specified directory
    inputs:path to directory
    '''
    import os
    import glob

    files = glob.glob(path)
    for f in files:
      os.remove(f)
    
