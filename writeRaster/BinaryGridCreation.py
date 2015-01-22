# -*- coding: utf-8 -*-
"""
This script was written in order to create binary grids that will be merged with tiles in the global 90m DEM, as a second band, to mark the spatial occurrence of void-filled cells.

Created by Natalie Robinson, 19 Oct., 2012.
"""
import os
import sys
import re
import osgeo
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import osr

def WriteRaster (raster,dst_filename,ncol,nrow,array):
        '''Create raster from array. This needs to be followed by gdal_translate command to set null value (I cannot get dataset.SetNoDataValue() to work)'''
        driver = raster.GetDriver()
        dst_ds = driver.Create(dst_filename, ncol, nrow,1,gdal.GDT_Int16)
        dst_ds.SetGeoTransform(raster.GetGeoTransform())
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326) #WGS84 lat long.
        dst_ds.SetProjection( srs.ExportToWkt() )
        dst_ds.GetRasterBand(1).WriteArray(array)
        format = 'EHdr'
        driver = gdal.GetDriverByName(format)
        dst_ds_new = driver.CreateCopy(dst_filename, dst_ds)
        dst_ds = None


def CreateBinary(InFile,OutPath,Coords):
     '''Convert input raster to array, then construct binary array where cells with 'nodata' value in input array get 1,
            all others get 0. Save binary array as raster with spatial reference info from input raster'''
     Ras=gdal.Open(InFile,GA_ReadOnly)
     cols=Ras.RasterXSize
     rows=Ras.RasterYSize
     Array=Ras.ReadAsArray(0,0,cols,rows)
     Binary=np.where(Array==-32768,1,0)
     WriteRaster(Ras,OutPath+'/Binary_'+Coords+'.bil',cols,rows,Binary)


#Set paths---------------------------------------------------------------------
FindFilesPath='/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/FilledDEMs'
AsterPath='/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2'
OutDir='/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/MetaDataDEMs'

#Loop through directory containing DEM's produced during DSF to get filenames, use these filenames to identify and process ASTER files for which 
# void-filling was completed as well as to name output binary rasters

for dirname, dirnames, filenames in os.walk(FindFilesPath):
    for filename in filenames:
        ext = os.path.splitext(filename)[1]
        if ext == ".bil":
            Coords=filename[3:23] #Get coordinates of void-filled
            for dname, dnames, fnames in os.walk(AsterPath):
                for fname in fnames:
                    ext = os.path.splitext(fname)[1]
                    if ext == ".bil" and fname[6:26]==Coords: #Find ASTER files with matching coordinates
                        CreateBinary(AsterPath + '/'+ fname,OutDir,Coords) #Create binary files where void pixels (which were filled) get 1
