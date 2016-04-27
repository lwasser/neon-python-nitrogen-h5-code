#!/usr/bin/python

##
# \file subset_aop_h5_file.py
# \brief This script will subset an L1 AOP H5 spectral radiance file, given an input
#        shape-shape file defining the clipping boundary.
#        Usage:
#            python subset_aop_h5_file.py -i inputfile.h5 -c clip.shp -o output.h5
#        -i / --input  : Required input h5 file.
#        -c / --clip   : Required input shp file.
#        -o / --output : Optional output parameter.  If omitted, "Subset_" is prepended to the input filename.
#
# \author Josh Elliott jelliott@neoninc.org
# \date 20 Oct 2015
# \version 1.0
# \updated 27 April 2016, Leah A Wasser
# Use: python subset_aop_h5_file.py --input NIS1_20140601_145336_atmcor.h5 --clip HarvardClipBox.shp --output newfile.h5

import os
from osgeo import ogr
from osgeo import osr
ogr.UseExceptions() # Throw exceptions so we can catch them properly.
import h5py as h5
import numpy as np
import argparse

##
# \class Subsetter
# \brief Subsetter class which will take an input h5 file, an shp file, and create a new
#        subsetted h5 file based on the input shp file.
#
class SubsetAOPh5:
    def __init__(self, h5File, shpFile, outputFile=''):
        self.rasterFile = h5File
        self.shapeFile = shpFile
        self.outputFile = outputFile
        if (len(outputFile) < 1):
            self.outputFile = os.path.join(os.path.dirname(h5File), 'Subset_' + os.path.basename(h5File))
        
        # Get polygon boundaries
        polygons, vectorSpatialRef = self.__GetPolygonsFromShapefile()
        
        # Open the file
        f = self.__OpenH5(self.rasterFile)
        
        # Get the coordinate system information
        rasterSpatialRef, mapInfo = self.__GetRasterSpatialRef(f)
        
        # Reproject the polygons to match the raster
        projectedPolygons = self.__ReprojectPolygons(polygons, vectorSpatialRef, rasterSpatialRef)
        
        # Get the map tie point and pixel size
        MapInfo = mapInfo.value[0].decode(encoding='utf_8').split(',')
        pixelSize = [float(i) for i in MapInfo[5:7]]
        pixelTiePoint = [float(i)-1.0 for i in MapInfo[1:3]] #Stored in 1-based pixel locations.  We want 0-based.
        mapTiePoint = [float(i) for i in MapInfo[3:5]]
        
        # Check for rotation
        hasRotation = "rotation" in MapInfo[-1]
        if hasRotation:
            theta = np.float64(MapInfo[-1].split('=')[-1])
            projectedPolygons = self.__TransformPolygons(-theta, projectedPolygons.copy(), mapTiePoint)
            
        # Get the bounding box of the polygon.
        boundingBox = self.__GetBoundingBox(projectedPolygons)
        
        # [xmin, ymax] is the upper-left point of the raster.  This is the new map tie point.
        # Insert this into MapInfo string, which we will write to the new file.
        newMapTiePoint = [str(boundingBox[0]), str(boundingBox[3])]
        if hasRotation:
            newMapTiePoint = self.__TransformPoint(theta, newMapTiePoint, mapTiePoint)
            
        # Create the new MapInfo string, with the new tie point.
        MapInfo[3:5] = [str(newMapTiePoint[0]), str(newMapTiePoint[1])]
        MapInfo = ','.join(MapInfo)
        
        # Get the pixel space bounding box.
        boundingBox = self.__GetPixelBoundingBox(boundingBox, pixelSize, pixelTiePoint, mapTiePoint)
        
        # Determine which datasets to subset.
        rasters, notRasters = self.__GetDatasetKeys(f)
        
        # new file
        fsubset = h5.File(self.outputFile, "w")
        
        # copy all non-rasters into the new file, except "map info", do that separately.
        for notRaster in notRasters:
            if 'map info' not in notRaster:
                newdataset = fsubset.create_dataset(notRaster, f[notRaster].shape, data= f[notRaster])
                self.__CopyAttributes(f[notRaster], newdataset)
        subsetMap = fsubset.create_dataset('map info', mapInfo.shape, data=MapInfo)
        self.__CopyAttributes(mapInfo, subsetMap)
        
        # Subset each raster and add to the new file
        for raster in rasters:
            subset = f[raster][:,boundingBox[2]:boundingBox[3]+1,boundingBox[0]:boundingBox[1]+1]
            dset = fsubset.create_dataset(raster, subset.shape, data=subset, compression='gzip', compression_opts=8, chunks=True)
            self.__CopyAttributes(f[raster], dset)
            if (raster in 'Reflectance'):
                dset.attrs['Scale Factor'] = 10000.0
            
        # close the file
        fsubset.close()
        
    def __CopyAttributes(self, orig, copy):
        for att in orig.attrs:
            copy.attrs.create(att, data=orig.attrs[att])
        
    def __GetDatasetKeys(self, f):
        keys = f.keys()
        rasters = []
        notRasters = []
        for key in keys:
            dims = f[key].shape
            if len(dims) == 3:
                rasters.append(key)
            else:
                notRasters.append(key)
        return rasters, notRasters
        
    def __GetPixelBoundingBox(self, boundingBox, pixelSize, pixelTiePoint, mapTiePoint):
    
        xs = boundingBox[0:2]
        ys = boundingBox[2:4]
        newBoundingBox = np.zeros(shape=(4,), dtype=np.int64)
    
        newXs = []
        newYs = []
        for x in xs:
            delX = (x - float(mapTiePoint[0])) / pixelSize[0]
            newX  = pixelTiePoint[0] + delX
            newXs.append(newX)
        newBoundingBox[0:2] = [ int(round(x)) for x in newXs ] # round to integer pixel locations
        for y in ys:
            delY = (y - float(mapTiePoint[1])) / pixelSize[1]
            newY = pixelTiePoint[1] - delY
            newYs.append(newY)
        newBoundingBox[3] = int(round(newYs[0])) # reverse order
        newBoundingBox[2] = int(round(newYs[1]))
        
        return newBoundingBox
    
    def __GetBoundingBox(self, polygons):
        # Collect the x and y min/max and return [xmin, xmax, ymin, ymax]
        boundingBox = np.zeros(shape=(4,), dtype=np.float64)
        
        isFirstPoint = True
        
        for polygon in polygons:
            for point in polygon:
                X = point[0]
                Y = point[1]
                
                if isFirstPoint:
                    boundingBox[0] = X
                    boundingBox[1] = X
                    boundingBox[2] = Y
                    boundingBox[3] = Y
                    isFirstPoint = False
                else:
                    if X < boundingBox[0]:
                        boundingBox[0] = X
                    elif X > boundingBox[1]:
                        boundingBox[1] = X
                    if Y < boundingBox[2]:
                        boundingBox[2] = Y
                    elif Y > boundingBox[3]:
                        boundingBox[3] = Y
        
        return boundingBox
            
    def __GetPolygonsFromShapefile(self):
        # First, get the GDAL/OGR driver for reading shapefiles.
        driver = ogr.GetDriverByName('ESRI Shapefile')
        # Have the driver open the file.
        dataSource = driver.Open(self.shapeFile)
        # Get the layer
        layer = dataSource.GetLayer()
        
        # Get the points from the geometry
        polygons = []
        for feat in layer:
            geom = feat.GetGeometryRef()
            ring = geom.GetGeometryRef(0)
            
            points = ring.GetPointCount()
            ps = []
            for p in range(points):
                point = ring.GetPoint_2D(p)
                ps.append(point)
            polygons.append(ps)
            
        # Get the Spatial Reference object (i.e. the map projection info) from the Layer.
        spatialRef = layer.GetSpatialRef()
        
        return polygons, spatialRef
    
    def __OpenH5(self, h5File):
        return h5.File(h5File, 'r') # read only
    
    def __GetRasterSpatialRef(self, f):
        css = f['coordinate system string']
        mapInfo = f['map info']
        rasterSpatialRef = osr.SpatialReference()
        rasterSpatialRef.ImportFromWkt(css[0].decode(encoding='utf_8'))
        return rasterSpatialRef, mapInfo
        
    def __ReprojectPolygons(self, polygons, sourceSpatialRef, targetSpatialRef):
        transform = osr.CoordinateTransformation(sourceSpatialRef, targetSpatialRef)
        outputPolygons = []
        for polygon in polygons:
            outputPolygon = []
            for point in polygon:
                wkt = "POINT (" + str(point[0]) + " " + str(point[1]) + ")"
                newPoint = ogr.CreateGeometryFromWkt(wkt)
                newPoint.Transform(transform)
                outputPolygon.append([newPoint.GetX(), newPoint.GetY()])
            outputPolygons.append(outputPolygon)
        return outputPolygons
    
    def __TransformPolygons(self, theta, polygons, tiePoint):
        outputPolygons = []
        for polygon in polygons:
            outputPolygon = []
            for point in polygon:
                transformedPoint = self.__TransformPoint(theta, point, tiePoint)
                outputPolygon.append(transformedPoint)
            outputPolygons.append(outputPolygon)
        return outputPolygons
    
    def __TransformPoint(self, theta, point, tiePoint):
        radians = np.radians(theta)
        r00 = np.cos(radians)
        r01 = -np.sin(radians)
        r10 = -r01
        r11 = r00
        x = tiePoint[0]
        y = tiePoint[1]
        T1 = np.matrix([
                       [1.0, 0.0, x],
                       [0.0, 1.0, y],
                       [0.0, 0.0, 1.0]
                       ], 
                      dtype=np.float64)
        T2 = np.matrix([
                       [1.0, 0.0, -x],
                       [0.0, 1.0, -y],
                       [0.0, 0.0, 1.0]
                       ], 
                      dtype=np.float64)
        R = np.matrix([
                       [r00, r01, 0.0],
                       [r10, r11, 0.0],
                       [0.0, 0.0, 1.0]
                       ], 
                      dtype=np.float64)
        p = np.matrix([[point[0]],[point[1]], [1.0]], dtype=np.float64)
        transformedPoint = T1 * R * T2 * p
        return [transformedPoint[0,0], transformedPoint[1,0]]

if __name__ == '__main__':
    
    # Parse input arguments.
    parser = argparse.ArgumentParser(description="AOP H5 Subsetter Program", add_help=True)
    parser.add_argument('-i', '--input', 
                        dest='inputFile',
                        required=True,
                        type=str,
                        help="Input file.  This file will be clipped by the shapefile.")
    parser.add_argument('-c', '--clip', 
                        dest='clipFile',
                        required=True,
                        type=str,
                        help="Shapefile to define the clipped area.")
    parser.add_argument('-o', '--output', 
                        dest='outputFile',
                        required=False,
                        default='',
                        type=str,
                        help="Optional. Output file location.  If omitted, 'Subset_' is prepended to output filename.")
    args = parser.parse_args()
    inputFile = args.inputFile
    clipFile = args.clipFile
    outputFile = args.outputFile
    
    # Call the subsetter
    SubsetAOPh5(inputFile, clipFile, outputFile=outputFile)
    