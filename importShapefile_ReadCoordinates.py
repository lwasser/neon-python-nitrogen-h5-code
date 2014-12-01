# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 17:23:00 2014

@author: lwasser
"""
#sudo pip install pyshp
#https://github.com/GeospatialPython/pyshp

import shapefile

#this is the data that i want to read in.
#F:\ESA_WorkshopData\WorkingDirectory\Field_SHP_Use
#SJERPlotCentroids_Buff_Square.shp

#plotBoundariesPath=(r'F:\ESA_WorkshopData\WorkingDirectory\Field_SHP_Use\SJERPlotCentroids_Buff_Square.shp')
#for mac
plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')



sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()

#get the coordinates of the third polygon
dd=shapes[3].bbox

#read all of the fields in the shapefile
sf.fields

#how many polygons are in the file?
len(shapes)
s=3
#give me the info for the third polygon
sf.record(3)

print "That's All Folks!"