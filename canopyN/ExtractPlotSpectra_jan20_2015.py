# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 17:16:27 2014
This code will run through a directory of H5 files and will extract 
a. metadata
@author: lwasser
"""
###############################################
#Import Required Functions
###############################################

import h5py 
import shapefile
import numpy as np

from writeGeotiff import writeGeotiff

#set working directory
import os
os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN')

#define the following paths
#the path where the h5 files will be stored
plotH5FilePath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/h5/'
plotH5_BrightPixPath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/brightPixelsH5/'
#the path where the best pixels to be used in analysis will be stored

#enter the directory that you wish to explore

#external hard drive - mac
#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')
fileDirectory = (r'F:/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')

#get a list of all files in the directory
from getFileList import geth5FileList
onlyH5files=geth5FileList(fileDirectory)

#Build a lookup of key metadata attributes for h5 files
finalLookup=[]   
from os.path import join
#iterate through all H5 files in the  directory and build a list of the
#filename, extents and mapinfo
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

#for mac
#plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
plotBoundariesPath=(r'C:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/sjerPlots/SJERPlotCentroids_Buff_Square.shp')

#read shapefile data
sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()

#read all of the fields in the shapefile
plotMetadata=sf.fields
records = sf.records()
#Create dictionary object that will store final data
plotIdDict={}


#loop through all plots
#find the flightlines that completely overlap (intersect) the with the plot boundary
#note: there could be an intersect command - look into that.

#create a disctionary of plot boundary coordinates
plotBound={}
#plotBound contains the key (plot id) and the 4 corners of the plot 
# bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
for j in xrange(len(shapes)):
    #get the coordinates of the plot boundary
    
    plotVertices=shapes[j].bbox
    #grab plot centroid coords
    plotCentroidX=float(records[j][3])
    plotCentroidY=float(records[j][2])
    
    #finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT
    #loop through all flightlines - figure out which ones contain the plot boundary

    print(j)
    print(records[j][0])

    #if they create the boundary, then store that in the disctionary  
    #plotID
    isInTemp=[]
    for i in xrange(len(finalLookup)):
    #for i in xrange(1):	
        print i
        if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
            #add the flightline index, the extents of the flightline and the plot centroid to the dict									
            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4],finalLookup[i][6],finalLookup[i][7]])

	   #This dictionary contains two lists. the first list is the flightline extents and the centroid (6 numbers)
	   #the second list is the X,Y lower left hand corner of the plot.		
        plotIdDict[records[j][0]]=[isInTemp,plotVertices]
        plotBound[records[j][0]]=plotVertices     

								
print('plotIdDict is working properly')							


plotNamesList=plotIdDict.keys()

#loop through each plot and find the best flightline (closest to the center)
#this code doesn't work properly so i'm bypassing it for the time being
#with a manual approach. to be reassessed later.

###
#import table of best flightlines

###

import csv
f = open('inputs/SJERTiles.txt')
csvRead=csv.reader(f)
next(csvRead)

disDict={}
for row in csvRead:
    disDict[row[0]]=(row[1],row[2])
    
print("Done Inventoring Data & Identifying Needed Flightlines!")


####################################
#Finally, extract subset from spectrometer data!

###################################

from cleanOutDir import cleanOutDir

#first clear out the H5 directory
cleanOutDir(plotH5FilePath + '*')

for keys in disDict: 
    print(keys)
    #create empty H5 File - this is where all of the plot data will be stored
    hFile = h5py.File('data/h5/' + keys + '.h5', 'a')  
    #get the flightline that needs to be subsetted
    filePath =(fileDirectory + disDict[keys][1])    
    file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode

    #Select the reflectance dataset within the flightline 
    reflectance=file['/Reflectance']

    #get flightline ID	
    flID=	int(disDict[keys][0])	
    # Grab the lower left corner of the flightline from the original flightline lookup table
    flLowerCorner= [finalLookup[flID][3],finalLookup[flID][1]]
    
    # Define / Calculate subset reflectance data from the flightline based upon plot boundary			
    SubsetCoordinates=[int(plotBound[keys][0]-flLowerCorner[0]),int(plotBound[keys][2]-flLowerCorner[0]),
                       int(flLowerCorner[1]-plotBound[keys][3]),int(flLowerCorner[1]-plotBound[keys][1])]
			
    numBands=len(reflectance)
    #Define the final slice from the flightline      
    plotReflectance=reflectance[0:numBands,SubsetCoordinates[2]:SubsetCoordinates[3],SubsetCoordinates[0]:SubsetCoordinates[1]]   
    
    #grp = hFile.create_group("Reflectance")
    hFile['Reflectance'] = plotReflectance
    file.close()
    hFile.close()

#create list of plot level H5 files
plotH5files=geth5FileList(plotH5FilePath)

################### part 3 ####################################
#run through each file, process NDVI, determine brightest pixels
#create H5 file per plot of bright pixels (for final processing)

#cleanout h5 files with brightest pixels
###############################################################


##########################3
#process NDVI
#
#########################

#clear out the bright pixels H5 directory
cleanOutDir(plotH5_BrightPixPath+'*')

from processNDVI import processNDVI
from extractBrightestPixels import findBrightPixels

NDVIdict={}   
brightPixels=[]
for file in plotH5files:
    brightPixels=[]
    filePath =(plotH5FilePath + file) 
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the flightline 
    reflectance=H5file['/Reflectance']
    
    ndviOut=processNDVI(reflectance)
    #get plot name
    if file.endswith('.h5'):
      plot = file[:-3]
    print plot
    #write the NDVI out as a geotif!
    filename=('NDVItiff/' + plot + '.tif' )
    writeGeotiff(filename,ndviOut,plotBound[plot][0],plotBound[plot][3])
    #create dictionary of NDVI values for kicks
    NDVIdict[plot]=ndviOut
    brightestBool=ndviOut>.6
    #lastly, extract brightest pixels
    brightPixels=findBrightPixels(reflectance,brightestBool)
    
    #create H5 file that will store the plot level spectra (brightest pixels)
    hFile = h5py.File('data/brightPixelsH5/bri' + plot + '.h5', 'a')  
    #grp = hFile.create_group("Reflectance")
    hFile['Reflectance'] = brightPixels
    H5file.close()
    hFile.close()
    

#np.sum(array) use this to count the number of true responses in an array

############################
#the next chunk of code will process canopy N using NDNI
#(and whatever other calcs we want to use)
###########################

#Calculate NDNI on just the brightest pixels
#NDNI = [log(1/R1510)-log (1/R1680)] / [log (1/R1510) + log (1/R1680)])

#create list of plot level H5 files
briPixH5Path = 'c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/brightPixelsH5/'

briPixH5Files=geth5FileList(briPixH5Path)
import math

for file in briPixH5Files:
    
    filePath =(briPixH5Path + file) 
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the flightline 
    reflectance=H5file['/Reflectance']
    b1=(reflectance[224,:]).astype('float')
    b2=(reflectance[258,:]).astype('float')
    NDNI=(np.log(b1)-np.log(b2)) / ((np.log(b1)+np.log(b2)))

    



















####################################
#OPTIONAL - quick plot to test that this is working!!
#####################################

#turn all of the lists into one list of numbers to plot a histogram of the data.
import itertools
list2d = plotReflectance
merged = list(itertools.chain.from_iterable(list2d))


import pyplot as plt
plt.hist(merged)
plt.title("Histogram")
plt.xlabel("Reflectance")
plt.ylabel("Frequency")

#render a quick image
plt.imshow(plotReflectance)
    

    #format the data just like the AOP data are formatted
    #groupName='/Reflectance'
    #print(groupName)				
    #check to see if this group already exists
    #if plotData[groupName]:			
	#del plotData[groupName]
    #plotData[groupName] = plotReflectance_Sub
    #newdict[groupName]	= plotReflectance_Sub
    

print "That's All Folks!"

    #subset out reflectance
    #plotReflectance=reflectance[50:60,3000:4000,300:600]  
	