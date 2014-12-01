# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 20:13:35 2014

@author: law
"""
#import libraries that Python needs to read shapefiles
import shapefile
import h5py 
import numpy

#first get the plot coordinate

#plotBoundariesPath=(r'F:\ESA_WorkshopData\WorkingDirectory\Field_SHP_Use\SJERPlotCentroids_Buff_Square.shp')
#for mac
plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()

#get the coordinates of the third polygon
# bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]

plotVertices=shapes[0].bbox

#read all of the fields in the shapefile
plotMetadata=sf.fields

#finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT

#next look at a file extent and determine whether the plot is in the extent for the flightline
#finalLookup
#i=9

#take a plot and figure out which flightlines the plot is in.
isInFlightLine=[]
for i in xrange(len(finalLookup)):
    print(i)
    if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
        print("in X and Ybounds")
        isInFlightLine.append(i)
        here=(finalLookup[i][3]-plotVertices[0],finalLookup[i][4]-plotVertices[2])
        here2=((plotVertices[1] - finalLookup[i][2]),(finalLookup[i][1]-plotVertices[3]))
        
        #numpy.mean()
        
#    if (plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1]):
#        print("in Y bounds")
        
                    
    
    

