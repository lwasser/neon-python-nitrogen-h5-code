# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 17:16:27 2014

@author: lwasser
"""


#import libraries that Python needs to read shapefiles
import h5py 
import numpy as np
import shapefile


#enter the directory that you wish to explore
#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')


#get a list of all files in the directory
from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir(fileDirectory) if isfile(join(fileDirectory,f)) ]

#just pull out the files that are h5 files (ignore other extensions)
onlyH5files=[]
for f in onlyfiles:
  if f.endswith(".h5"):
    onlyH5files.append(f)
    
#should be able to populate this ahead of time with Nan
finalLookup=[]   
#for f in onlyH5files:
    #iterate through all H5 files in the directory
for f in xrange(len(onlyH5files)):
    #open the file name to the directory path so the code knows where to find
    #the hdf5 file to open.
    filePath=join(fileDirectory,onlyH5files[f])
    #open hdf5 file  
    file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the H5 file and associated needed attributes. 
    reflectance=file['/Reflectance']
    CRS=file['/coordinate system string']
    mapInfo=['/map info']
    
    #Split map info string to extract raster corner location
    mapInfo=str(file['map info'][:]).split(',')
    eastingUL=float(mapInfo[3])
    northingUL=float(mapInfo[4])
    xsize=float(mapInfo[5])
    ysize=float(mapInfo[6])
    zone=int(mapInfo[7])
    
    #grab the shape of the reflectance matrix (the raster size) 
    #Use this to define raster x,y,z extent (matrix dimensions)
    nb,nY,nX=reflectance.shape
    
    #find the extents of the hdf5 file
    yTop=northingUL
    yBot=northingUL-nY*ysize
    xLeft=eastingUL
    xRight=eastingUL+nX*xsize
    
    #find file centroid
    yCent=yBot+(nY/2)
    xCent=xLeft+(nX/2)

    #be sure to close the file
    file.close() 

    #write out elements into a list
    fileExtents=[onlyH5files[f],yTop,yBot,xLeft,xRight,mapInfo,xCent,yCent]  
    finalLookup.append(fileExtents)

#%reset clears all variables
print("All Files Inventoried - finalLookup Table Created!")




###########################################################################
# PART TWO -- Find flightlines for each plot
###########################################################################

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

#loop through all plots
for j in xrange(len(shapes)):
    #get the coordinates of the plot boundary
    #bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
    plotVertices=shapes[j].bbox
    #grab plot centroid coords
    plotCentroidX=float(records[j][3])
    plotCentroidY=float(records[j][2])
    
    #finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT
    #loop through all flightlines - figure out which ones contain the plot boundary
      
    #plotID
    isInTemp=[]
    for i in xrange(len(finalLookup)):  
        if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4]])
        plotIdDict[records[j][0]]=[isInTemp]



########################################################################
#try to plot things
########################################################################

import matplotlib
import matplotlib.pyplot as plt

onePlot=plotIdDict['SJER1068'][0]

#create the figure
fig = plt.figure()
ax = fig.add_subplot(111)

for i in xrange(len(onePlot)): 
    print(i)
    xWidth=(onePlot[i][5]-onePlot[i][4])
    yHeight=(onePlot[i][2]-onePlot[i][3])
    locals()["rect"+str(i)] = matplotlib.patches.Rectangle((onePlot[i][4],onePlot[i][3]), xWidth, yHeight, fill=None, edgecolor='red')
    ax.add_patch(locals()["rect"+str(i)])
    #ax.add_patch(matplotlib.patches.Rectangle((onePlot[i][4],onePlot[i][2]), xWidth, yHeight, edgecolor='violet'))

#add plot boundary
#bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
plotVertices=shapes[0].bbox 
plotBoundary = matplotlib.patches.Rectangle((plotVertices[0],plotVertices[1]), 40, 40, edgecolor='blue', facecolor='white')
ax.add_patch(plotBoundary)  
    
plt.xlim([250000, 265000])
plt.ylim([4104000, 4115000])
plt.show()


fig = plt.figure()
ax = fig.add_subplot(111)
rect1 = matplotlib.patches.Rectangle((0,0), 200, 800, color='yellow')
rect2 = matplotlib.patches.Rectangle((100,150), 170, 700, color='red')
rect3 = matplotlib.patches.Rectangle((50,100), 180, 800, color='#0099FF')
#circle1 = matplotlib.patches.Circle((-200,-250), radius=90, color='#EB70AA')
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_patch(rect3)
#ax.add_patch(circle1)
plt.xlim([-100, 1000])
plt.ylim([-100, 1000])
plt.show()