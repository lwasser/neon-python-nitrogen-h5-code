# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 20:13:35 2014

@author: law
"""
#import libraries that Python needs to read shapefiles
import shapefile
import h5py 
import numpy as np

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
#isInFlightLine=[records[0][0]]
isInFlightLine=[]

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
#calculate number of tiles to sort through								
numOfTiles=(len(isInFlightLine)-1) 
distanceToTileCenter=[]
	
for j in xrange(len(isInFlightLine)):							
	tileNum=isInFlightLine[j]
	#find tile center							
	tileCentroidX = finalLookup[tileNum][6]
	tileCentroidY = finalLookup[tileNum][7]
						
	dist = np.sqrt( (plotCentroidX - tileCentroidX)**2 + (plotCentroidY - tileCentroidY)**2 )							
	distanceToTileCenter.append(dist)
	
np.amin(distanceToTileCenter)
	
								


#questions to ask greg
#how do you prepulate a matrix? 
#matrix vs list
#how do you look through skipping the first few cells e.g. (2:4)
#a min on a column of values?

#want to create a matrix
#PLOTID  value-tile num value - distance from center	

#ask josh - he will have a solution.							
                   
    
    

