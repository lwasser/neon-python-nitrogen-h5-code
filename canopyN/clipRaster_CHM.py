# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 08:54:19 2015

The functions in this code 

find_pixel_no - this little function will take xy coordinates and indentify the array location 
in the raster based upon geographic coordinates.

clipRaster: this function takes an input raster and a clip extent and produces
an array that is the final clipped raster. The array can be saved as a geotiff if needed.

@author: lwasser
"""


from osgeo import gdal, gdalconst
import sys
from writeGeotiff import writeGeotiff

def find_pixel_no(pt,corner,res,maxloc):
    '''
    This little function finds the pixel location in the raster where the 
    xy coordinates result in. 
    '''
    loc=(pt-corner)/res
    loc=min(maxloc,int(loc))
    return max(loc,0)

def clipRaster(inputRaster,clipExtent):
    '''
    This function will take an input raster path, will open it, and clip out the
    needed extent using a list of corner coordinates of a rectangular or square region.
    It will output an array which can be written to a raster if needed
    
    Inputs: Raster path, clipExtent: list of corner coordinates [leftx, rightx, topy, bottomy]
    '''



    #open raster
    ds = gdal.Open(inputRaster, gdalconst.GA_ReadOnly)

    #make sure the data is opened
    if ds is None:
        print "Could not open {0}".format(inputRaster)
        sys.exit(-1)

    #get X,Y size of the raster
    nrows=ds.RasterYSize
    ncols=ds.RasterXSize

    #get spatial attributes of file
    geotransform=ds.GetGeoTransform()
    topleftcorner = [geotransform[0],geotransform[3]]
    datares = [ geotransform[1], geotransform[5]]    

    #crop the raster by determining the pixel location for the crop


    xLeft = find_pixel_no(clipExtent[0], topleftcorner[0], datares[0],ncols)
    xRight = find_pixel_no(clipExtent[1], topleftcorner[0], datares[0],ncols)
    yTop = find_pixel_no(clipExtent[2], topleftcorner[1], datares[1],nrows)
    yBottom = find_pixel_no(clipExtent[3], topleftcorner[1], datares[1],nrows)

    #now read the dataset in as an array slicing just the plot region of the data
    data=ds.ReadAsArray(xLeft, yTop, xRight-xLeft, yBottom-yTop)

    # close raster
    ds = None
    return data
    
# writeGeotiff (dst_filename,array,upperLeftx,upperLeftY,EPSG,ncol=40,nrow=40):
#writeGeotiff('chmTiff/test423.tif',data,lx,ty,32611)