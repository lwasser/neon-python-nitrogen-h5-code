# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 13:55:05 2014
This code will take a set of coordinates and find the spectral and spatial subset in a particular HDF5
file
@author: law
"""
#import libraries that Python needs to read shapefiles
import shapefile
import h5py 


#import plot boundary layer
#plotBoundariesPath=(r'F:\ESA_WorkshopData\WorkingDirectory\Field_SHP_Use\SJERPlotCentroids_Buff_Square.shp')
#for mac
plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')


sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()

#get the coordinates of the third polygon
# bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
#[256156.94700000063, 4108732.0260000043, 256196.9469999997, 4108772.0260000005]

plotVertices=shapes[0].bbox

#read all of the fields in the shapefile
plotMetadata=sf.fields

#python starts indexing at 0 silly goat
lowerCorner=[255273.00, 4113098.0]

#%%

#Read in File - remember paths are different mac vs pc
#filePath = (r'F:\D17_Data_2014_Distro\02_SJER\SJER_Spectrometer_Data\2013061320\Reflectance\NIS1_20130613_134931_atmcor.h5')
filePath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/NIS1_20130613_141829_atmcor.h5')

file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode


#Select the reflectance dataset    
reflectance=file['/Reflectance']
CRS=file['/coordinate system string']
mapInfo=['/map info']

# inthe data its band, Y, X)
#Testing=reflectance[54,3000:4000,300:600]   

#calculate subsetBoundaries
#subsetLeftX=plotVertices[0]-lowerCorner[0]
#subsetRightX=plotVertices[2]-lowerCorner[0]
#subsetBottomY=lowerCorner[1]-plotVertices[1]
#subsetTopY=lowerCorner[1]-plotVertices[3]

#SubsetCoordinates[subsetLeftX, SubsetRightX, SubsetBottomY, SubsetTopY]
#int seems to round down... need to think about how to do this... 
SubsetCoordinates=[int(plotVertices[0]-lowerCorner[0]),int(plotVertices[2]-lowerCorner[0]),int(lowerCorner[1]-plotVertices[1]),int(lowerCorner[1]-plotVertices[3])]

# need to round the above so it's integers instead of floating point.
plotReflectance_Sub=reflectance[54,SubsetCoordinates[3]:SubsetCoordinates[2],SubsetCoordinates[0]:SubsetCoordinates[1]]   

#create empty file
plotData = h5py.File('data/SJERPlotRefl3.h5', 'a')   #a is read / write  
#assign the reflectance values to a group

#assign extents to h5 file (testing)
where=plotData.create_group('where')
where.attrs['LL_lat']=plotVertices[0]
where.attrs['LL_lon']=plotVertices[1]
where.attrs['UR_lat']=plotVertices[2]
where.attrs['UR_lon']=plotVertices[3]
#where.attrs['LL_lat']=37.10998365460052
#where.attrs['LL_lon']=-119.74120827591719
#where.attrs['UR_lat']=37.11269255881616
#where.attrs['UR_lon']=-119.73676741348389
where.attrs['projdef']='+proj=utm +zone=11 +ellps=WGS84 +datum=WGS84'
where.attrs['xscale']=1.0
where.attrs['yscale']=1.0
where.attrs['xsize']=1.0
where.attrs['ysize']=1.0


#LL_lat = 37.10998365460052
#LL_lon = -119.74120827591719
#UR_lat = 37.11269255881616
#UR_lon = -119.73676741348389

#del plotData['plotOne']
plotData['plotOne'] = plotReflectance_Sub

file.close()
plotData.close()

print "That's All Folks!"


#reflectance [spectral,x,y] -- not sure about y x order yet.
