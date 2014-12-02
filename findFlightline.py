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
records = sf.records()
#to access attribute data records[0][2:3]

#grab plot centroid coords
plotCentroidX=float(records[0][3])
plotCentroidY=float(records[0][2])

#finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT

#next look at a file extent and determine whether the plot is in the extent for the flightline
#finalLookup
#i=9

#take a plot and figure out which flightlines the plot is in.
isInFlightLine=[records[0][0]]
for i in xrange(len(finalLookup)):
    print(i)
    if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
        print("in X and Ybounds")
        isInFlightLine.append(i)
        #here=(finalLookup[i][3]-plotVertices[0],finalLookup[i][4]-plotVertices[2])
        #here2=((plotVertices[1] - finalLookup[i][2]),(finalLookup[i][1]-plotVertices[3]))

#now loop through each flightline and find which one is center
        
        #numpy.mean()
        
#    if (plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1]):
#        print("in Y bounds")
        
#calculate distance         
#        dist = sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
        
                    
    
    

