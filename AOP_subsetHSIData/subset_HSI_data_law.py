from osgeo import ogr
from osgeo import osr
ogr.UseExceptions() # Throw exceptions so we can catch them properly.
import h5py as h5
import numpy as np
import os
# from matplotlib import pyplot as plt

def CopyAttributes(orig, copy):
    for att in orig.attrs:
        copy.attrs.create(att, data=orig.attrs[att])

def GetPolygonsFromShapefile(shapeFile):
    # Get the TOS polygon shapefile
    # First, get the GDAL/OGR driver for reading shapefiles.
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # Have the driver open the file.
    dataSource = driver.Open(shapeFile)
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

def ReprojectPolygons(polygons, sourceSpatialRef, targetSpatialRef):
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

def TransformPolygons(theta, polygons, tiePoint):
    outputPolygons = []
    for polygon in polygons:
        outputPolygon = []
        for point in polygon:
            transformedPoint = TransformPoint(theta, point, tiePoint)
            outputPolygon.append(transformedPoint)
        outputPolygons.append(outputPolygon)
    return outputPolygons

def TransformPoint(theta, point, tiePoint):
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

def GetBoundingBox(polygons):
    # Collect the projected x and y min/max and return [xmin, xmax, ymin, ymax]
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

def GetPixelBoundingBox(boundingBox, pixelSize, pixelTiePoint, mapTiePoint):
    
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
        newY = pixelTiePoint[1] - delY # this was = delY and was causing a negative value
        newYs.append(newY)
    newBoundingBox[3] = int(round(newYs[0])) # reverse order
    newBoundingBox[2] = int(round(newYs[1]))

    # check the min and max values; added 4/27
    # check x min and max values, ensure they are within the index boundaries
    if newBoundingBox[0] < 0:
        newBoundingBox[0] = 0
    if newBoundingBox[1] > xyDims[1]:
        newBoundingBox[1] = xyDims[1]
        
    # check the min and max values 
    # check Y min and max values, ensure they are within the index boundaries
    if newBoundingBox[2] < 0:
        newBoundingBox[2] = 0
    if newBoundingBox[3] > xyDims[0]:
        newBoundingBox[3] = xyDims[0]
    
    return newBoundingBox

def GetDatasetKeys(f):
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

def RotationTest(theta, polygons, tiePoint):
    rotatedPolygons = TransformPolygons(-theta, polygons.copy(), mapTiePoint)
    xs = []
    ys = []
    for polygon in rotatedPolygons:
        for point in polygon:
            xs.append(point[0])
            ys.append(point[1])
    return xs, ys
  
# edit below to adjust files  
if __name__ == '__main__':
    inputDir= r'/Users/lwasser/Documents/data/1_spectrometerData/Teakettle'
    #inputDir = r'C:\Users\jelliott\Desktop\Hackathon\SJERClip'
    shapefile = os.path.join(inputDir, 'teakettleClip_2.shp')       
    #shapefile = os.path.join(inputDir, 'SJERClip_UTM11N.shp')
    rasterFileBase ='NIS1_20130614_100459_atmcor.h5'
    #rasterFileBase ='NIS1_20130614_095740_atmcor.h5'
    #rasterFileBase = 'NIS1_20130613_143801_atmcor.h5'
    rasterFile = os.path.join(inputDir, rasterFileBase)
    outputFile = os.path.join(inputDir, 'Subset3' + rasterFileBase)
    
    # Get polygon boundaries
    polygons, vectorSpatialRef = GetPolygonsFromShapefile(shapefile)
    
    # Open the file
    f = h5.File(rasterFile, "r")
    reflectance = f['Reflectance']
    css = f['coordinate system string']
    mapInfo = f['map info']
    fwhm = f['fwhm']
    wavelength = f['wavelength']
    # get the y max abd x max pixel index values
    xyDims = reflectance.shape[1:3]
    
    # Transform clipping polygons
    rasterSpatialRef = osr.SpatialReference()
    rasterSpatialRef.ImportFromWkt(css[0].decode(encoding='utf_8'))
    # Leah Note: there is a minor difference in coordinates after the reprojection
    projectedPolygons = ReprojectPolygons(polygons, vectorSpatialRef, rasterSpatialRef)
    
    # Get the map tie point and pixel size
    MapInfo = mapInfo.value[0].decode(encoding='utf_8').split(',')
    pixelSize = [float(i) for i in MapInfo[5:7]]
    pixelTiePoint = [float(i)-1.0 for i in MapInfo[1:3]] # Stored in 1-based pixel locations.  We want 0-based.
    mapTiePoint = [float(i) for i in MapInfo[3:5]]
    
    # TEST: Rotation test
    '''
    syms = ['.','o','v', '^', '*']
    for theta in range(0, 360, 2):
        xs, ys = RotationTest(-float(theta), projectedPolygons, mapTiePoint)
        plt.plot(xs, ys, syms[int(theta/2) % 5])
    plt.show()
    '''
       
    
    # Check for rotation
    hasRotation = "rotation" in MapInfo[-1]
    if hasRotation:
        theta = np.float64(MapInfo[-1].split('=')[-1])
        projectedPolygons = TransformPolygons(-theta, projectedPolygons.copy(), mapTiePoint)

    # Get the bounding box of the polygon in UTM.
    boundingBoxUTM = GetBoundingBox(projectedPolygons)     
    
    # Get the pixel space bounding box.
    boundingBox = GetPixelBoundingBox(boundingBoxUTM, pixelSize, pixelTiePoint, mapTiePoint)
    
    
    
    # [xmin, ymax] is the upper-left point of the raster.  This is the new map tie point.
    # Insert this into MapInfo string, which we will write to the new file.
    
    # Currently this code reassigns the Tie point to the tie point of the clip
    # polygon. however, it really needs to check first whether the polygon is
    # within the bounds of the data or not. 
    
    # new tie point should be calculated using the original tie point and then
    # counting over in UTM (or the defined CRS) to the new left corner pixel tie point
    # otherwise, the code doesn't account for pixel slivers.
    newMapTiePoint = [float('nan'),float('nan')]
    # calculate NEW x tie point using Original Data tie point as "0,0" reference
    newMapTiePoint[0] = mapTiePoint[0] + boundingBox[0] * pixelSize[0]
    # calculate NEW x tie point using Original Data tie point as "0,0" reference
    newMapTiePoint[1] = mapTiePoint[1] - boundingBox[2] * pixelSize[1]
    
    
    # newMapTiePoint = [str(boundingBox[0]), str(boundingBox[3])] #joshs old code
    if hasRotation:
        newMapTiePoint = TransformPoint(theta, newMapTiePoint, mapTiePoint)
     
    # can delete the code below because we shoulnd't need these checks if we calculate
    # this way
    # finally, check to ensure the newMaptTiePoint is not further north or west 
    # than the original data tie point 
    # If the clipping polygon x tie point value is LESS THAN the data tie point,
    # force the tie point to the data x tie point
    # if boundingBoxUTM[0] < float(MapInfo[3]):
    #    newMapTiePoint[0] = float(MapInfo[3])    

    # If the clipping polygon y tie point value is LESS THAN the data tie point,
    # force the tie point to the data x tie point
    # if boundingBoxUTM[3] > float(MapInfo[4]):
    #     newMapTiePoint[1] = float(MapInfo[4])    

    
    MapInfo[3:5] = [str(newMapTiePoint[0]), str(newMapTiePoint[1])]
    MapInfo = ','.join(MapInfo)
    
    # Determine which datasets to subset.
    rasters, notRasters = GetDatasetKeys(f)
    
    # new file
    fsubset =  h5.File(outputFile, "w")
    
    # copy all non-rasters into the new file, except "map info", do that separately.
    for notRaster in notRasters:
        if 'map info' not in notRaster:
            newdataset = fsubset.create_dataset(notRaster, f[notRaster].shape, data= f[notRaster])
            CopyAttributes(f[notRaster], newdataset)
    subsetMap = fsubset.create_dataset('map info', mapInfo.shape, data=MapInfo)
    CopyAttributes(mapInfo, subsetMap)
    
    # Subset each raster and add to the new file
    for raster in rasters:
        subset = f[raster][:,boundingBox[2]:boundingBox[3]+1,boundingBox[0]:boundingBox[1]+1]
        dset = fsubset.create_dataset(raster, subset.shape, data=subset, compression='gzip', compression_opts=8, chunks=True)
        CopyAttributes(f[raster], dset)
        if (raster in 'Reflectance'):
            dset.attrs['Scale Factor'] = 10000.0
        
    # close the file
    fsubset.close()
