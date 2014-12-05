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
#plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
plotBoundariesPath=(r'C:/Users/lwasser/Documents/GitHub/adventures-with-python/data/sjerPlots/SJERPlotCentroids_Buff_Square.shp')


sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()



#read all of the fields in the shapefile
plotMetadata=sf.fields
records = sf.records()
#to access attribute data records[0][2:3]
plotIdDict={}
isInFlightLine=[]

#loop through all plots
for j in xrange(len(shapes)):
    
    #get the coordinates of the plot boundary
    #bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
    plotVertices=shapes[j].bbox
    print(j)
    #grab plot centroid coords
    plotCentroidX=float(records[j][3])
    plotCentroidY=float(records[j][2])
    
    #finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT
    
    #loop through all flightlines - figure out which ones contain the plot boundary
      
    print(j)
    print(records[j][0])
    #plotID
    isInTemp=[]
    for i in xrange(len(finalLookup)):  
        print(i)
        if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
            print("in X and Y bounds")
            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4]])
            isInFlightLine.append([records[j][0],i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3]])
        plotIdDict[records[j][0]]=[isInTemp]


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
                   
    
    

