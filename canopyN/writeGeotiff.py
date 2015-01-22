# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 09:42:53 2015

@author: lwasser
"""

from osgeo import gdal
import osr
import os
#conda install gdal provides the above libraries.
os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/')

def writeGeotiff (dst_filename,array,upperLeftx,upperLeftY,ncol=40,nrow=40):
        '''Create raster from array. This needs to be followed by gdal_translate command to set null value 
        (I cannot get dataset.SetNoDataValue() to work)
        Inputs Raster??
        dst_filename: string wtih the file name output you want
        array: the input array to be converted
        ncol, nrow (defaults to 40)
        '''
        #driver = raster.GetDriver()
        driver = gdal.GetDriverByName('GTiff')
        #dst_ds = driver.Create(dst_filename, ncol, nrow,1,gdal.GDT_Int16)
        #create ea 32 bit floating point raster
        dst_ds = driver.Create(dst_filename, ncol, nrow,1,gdal.GDT_Float32)
        
         # You need to get those values like you did.
        #x_pixels = 16  # number of pixels in x
        #y_pixels = 16  # number of pixels in y
        PIXEL_SIZE = 1  # size of the pixel...        
        #x_min = 553648  
        #y_max = 7784555  # x_min & y_max are like the "top left" corner.
        
        #  Set the georeference info (top left corner included)
        #dst_ds.SetGeoTransform(raster.GetGeoTransform())
        dst_ds.SetGeoTransform((
        upperLeftx, PIXEL_SIZE,  # 1
        0, upperLeftY,
        0, -PIXEL_SIZE))   
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(32611) #UTM zone 11N
        
        dst_ds.SetProjection( srs.ExportToWkt() )
        dst_ds.GetRasterBand(1).WriteArray(array)
        #format = 'tif'
        #driver = gdal.GetDriverByName(format)
        #dst_ds_new = driver.CreateCopy(dst_filename, dst_ds)
        dst_ds = None
        #dst_ds.close()



#NDVIdict['SJER112']



def arrayToRaster(array):
    
    """Array > Raster
    Save a raster from a C order array.

    :param array: ndarray
    """
    dst_filename = '/NDVItiff/name.tiff'


    # Identify Tiff Dimensions and resolution.
    x_pixels = 20  # number of pixels in x
    y_pixels = 20  # number of pixels in y
    PIXEL_SIZE = 1  # size of the pixel...
    
    # x_min & y_max are like the "top left" corner.   
    x_min = 553648  
    y_max = 7784555  
    #wkt_projection = 'a projection in wkt that you got from other file'
    
    
    wkt_projection='PROJCS["UTM_Zone_11N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-117.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        dst_filename,
        x_pixels,
        y_pixels,
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform((
        x_min,    # 0
        PIXEL_SIZE,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -PIXEL_SIZE))  

    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    return dataset, dataset.GetRasterBand(1)  #If you need to return, remenber to return  also the dataset because the band don`t live without dataset.