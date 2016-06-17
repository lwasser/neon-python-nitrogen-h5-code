# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 19:49:31 2016

@author: law
"""
import os
import platform

# check to see what platform i'm running on
if platform.system() == 'Windows':
    #set basepath for windows
    basePath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN'
    fileDirectory = (r'G:/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
else:
    #path to MAC git repo
    basePath='/Users/LAW/Documents/DATA/'
    fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
    chmPath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_LiDAR_Data/CHM/r_filtered_CHM_pit_free.tif')

os.chdir(basePath)
os.getcwd()

import gdal

# open dataset
ds = gdal.Open('NEON-DS-Landsat-NDVI/HARV/2011/NDVI/005_HARV_ndvi_crop.tif')
print ds.GetMetadata()

# extract TOP LEFT corner coordinate

UpperLeft = [ds.GetGeoTransform()[0], ds.GetGeoTransform()[3]]
# get projection
ds.GetProjection()

def GDALInfoReportCorner(hDataset):
	'''Transform the point into georeferenced coordinates.
	Assuming the data are in UTM meters so you can simply ADD to calculate extent'''	
	adfGeoTransform = hDataset.GetGeoTransform(can_return_null = True)
	dfGeoX = adfGeoTransform[0] + (hDataset.RasterXSize * adfGeoTransform[1])
	dfGeoY = adfGeoTransform[3] - (hDataset.RasterYSize * adfGeoTransform[1])
	return [adfGeoTransform[0], dfGeoX, dfGeoY,adfGeoTransform[0]]

fileExtent = GDALInfoReportCorner(ds)	

# import libraries
from shapely.geometry import Polygon
anExtent = fileExtent	
def CreateExtent(anExtent):
	# create list of x and y min an max
	boundary = [[anExtent[0], anExtent[3]], [anExtent[1], anExtent[3]], 
		[anExtent[1], anExtent[2]], 
		[anExtent[0], anExtent[2]]]
	boundary = Polygon(boundary)	

# close dataset
ds = None

# if we need a proj 4 string.
import osr
import gdal
inDS = gdal.open(r'c:\somedirectory\myRaster.tif')
inSRS_wkt = inDS.GetProjection()  # gives SRS in WKT
inSRS_converter = osr.SpatialReference()  # makes an empty spatial ref object
inSRS_converter.ImportFromWkt(inSRS)  # populates the spatial ref object with our WKT SRS
inSRS_forPyProj = inSRS_converter.ExportToProj4()  # Exports an SRS ref as a Proj4 string usable by PyProj