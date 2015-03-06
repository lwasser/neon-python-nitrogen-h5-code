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
#set working directory
import os
os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN')

import h5py 
import numpy as np
from writeGeotiff import writeGeotiff
from clipRaster_CHM import clipRaster
from getFileList import geth5FileList
from os.path import join
from pandas import read_csv
from derivePlotBoundary import derivePlotBoundary
from processNDVI import processNDVI
from extractBrightestPixels import findBrightPixels

########################## DEFINE PATHS #################################
#########################################################################

basePath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN'
#the path where the h5 files will be stored
plotH5FilePath=basePath+ '/data/h5/'

#The path where the best pixels to be used in analysis will be stored
plotH5_BrightPixPath=basePath+'/data/brightPixelsH5/'
#NDVI tiff folder
NDVItiffpath = basePath+'/data/ndviTiff/'
#CHM tiff folder
CHMtiffpath = basePath+'/data/chmTiff/'

#external hard drive - mac
#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')
fileDirectory = (r'G:/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')

xyPlotLoc  = basePath+ '/fieldData/SJERPlotCentroids.csv'

##########################  #################################
#########################################################################



########################## INVENTORY H5 Files #################################
#########################################################################

#get a list of all files in the directory

onlyH5files=geth5FileList(fileDirectory)

#Build a lookup of key metadata attributes for h5 files
finalLookup=[]   
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


########################## Generate Plot Boundaries #########################
#############################################################################

#first get the plot coordinate

#for mac
#plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
#plotBoundariesPath=(r'C:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/sjerPlots/SJERPlotCentroids_Buff_Square.shp')

#import text file with plot name and x,y centroid.
p = open(xyPlotLoc)
dfPlotLoc = read_csv(p, header=0)

#create plot boundary dictionary
plotBound={}
plotCorners=[]
for index, row in dfPlotLoc.iterrows():
    xy= [row['easting'],row['northing']]
    plotCorners = derivePlotBoundary(xy[0], xy[1], 40, 40)
    #need to make sure the plotBoundary 
    #xy is a list of coordinates leftx, rightx, topy, bottomy
    plotBound[row['Plot_ID']]=[plotCorners,xy]


###########################################################################
#  Find flightlines for each plot
###########################################################################

#this should be redone to simply accept a csv with plot XY values.


#loop through all plots
#find the flightlines that completely overlap (intersect) the with the plot boundary

plotIdDict={}

#Plot vertices used to be:
# bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]

#grab list of plots
plotNamesList=plotBound.keys()    

#loop through plots and identify which fligthlines overlap which plots    
for plot in plotNamesList:
    #grab the vertices of the plot bounding box
    plotVertices=plotBound[plot][0]
    #plot vertices was: [left X, Lower Y, right X, Upper Y ]
    #it's now leftx, rightx, topy, bottomy
    plotLx = plotVertices[0]
    plotRx = plotVertices[1]
    plotTy = plotVertices[2]
    plotBy = plotVertices[3]
       
    #finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT
    #loop through all flightlines - figure out which ones contain the plot boundary

    #if they create the boundary, then store that in the disctionary  
    #plotID
    isInTemp=[]
    for i in xrange(len(finalLookup)):
    #for i in xrange(1):	
        print i
        if ((plotLx > finalLookup[i][3]) and (plotRx < finalLookup[i][4])) and ((plotBy > finalLookup[i][2]) and (plotTy < finalLookup[i][1])):
            #add the flightline index, the extents of the flightline and the plot centroid to the dict									
            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4],finalLookup[i][6],finalLookup[i][7]])

	   #This dictionary contains two lists. the first list is the flightline extents and the centroid (6 numbers)
	   #the second list is the X,Y lower left hand corner of the plot.		
        plotIdDict[plot]=[isInTemp,plotVertices]
        #plotBound[records[j][0]]=[plotVertices,[plotCentroidX, plotCentroidY]]

								
print('plotIdDict - A dictionary of h5 files for each plot is created')							


#loop through each plot and find the best flightline (closest to the center)
#this code doesn't work properly so i'm bypassing it for the time being
#with a manual approach (created a text file with the best flightline for each plot
# this to be reassessed later. when the data are mosaicked this will be less of an issue

####################################
#import table of best flightlines

###################################

import csv
f = open('inputs/SJERTiles.txt')
csvRead=csv.reader(f)
next(csvRead)

disDict={}
for row in csvRead:
    disDict[row[0]]=(row[1],row[2])
    
print("Done Inventoring Data & Identifying Needed Flightlines!")


####################################
#Extract spatial subset from spectrometer data
#one subset for each plot

###################################

from cleanOutDir import cleanOutDir

#first clear out the H5 directory
cleanOutDir(plotH5FilePath + '*')

#create H5 file with spectra for each plot - named with the plot name
for keys in disDict: 
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
    ###########################################################################
    ############################ FFFFIIIIXXXX THIS!!! ###################
    #the plot bound indices below need to be remapped again
    #plot vertices was: [left X, Lower Y, right X, Upper Y ]
    #it's now leftx, rightx, topy, bottomy
    
    # Define / Calculate subset reflectance data from the flightline based upon plot boundary			
    SubsetCoordinates=[int(plotBound[keys][0][0]-flLowerCorner[0]),int(plotBound[keys][0][1]-flLowerCorner[0]),
                       int(flLowerCorner[1]-plotBound[keys][0][2]),int(flLowerCorner[1]-plotBound[keys][0][3])]
			
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
#########################

#clear out the bright pixels H5 directory
cleanOutDir(plotH5_BrightPixPath+'*')
#clear out the NDVI geotiff folder
cleanOutDir(NDVItiffpath+'*')


# functions i created to calculate NDVI for each plot and extract
#only pixels that are "bright" (healthier veg)


NDVIdict={}   
brightPixels=[]

for file in plotH5files:
    brightPixels=[]
    filePath =(plotH5FilePath + file) 
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the flightline 
    reflectance=H5file['/Reflectance']
    
    #get plot name
    if file.endswith('.h5'):
      plot = file[:-3]
      
    #default NDVI bands redBand=53,NIRband=95, redEnd=57, NIRend=99
    ndviOut=processNDVI(reflectance)   
    
    #write the NDVI out as a geotif
    filenameNDVI=('data/NDVItiff/' + plot + 'NDVI.tif' )
    writeGeotiff(filenameNDVI,ndviOut,plotBound[plot][0][0],plotBound[plot][0][2])
   
    #create dictionary of NDVI values for kicks
    
    #NOTE: this is problematic now because of low NDVI values in some plots (senescent grass)
    #- might need to look at the lidar as well for this
    NDVIdict[plot]=ndviOut
    brightestBool=ndviOut>.6
    
    #check to see how many bright pixels are in the tiff
    print plot, 'brightpixels: ', (np.count_nonzero(brightestBool))

    #delete testing1=reflectance    
    #to save code, simply apply all non  bright pixels (boolean= false) to -999  
    #not sure how to do the above gracefully  
    #delete testing=reflectance[:,:,brightestBool] = -999
    
    #lastly, extract brightest pixels
    brightPixels=findBrightPixels(reflectance,brightestBool)
    
    ########## export CSV for convolution    ###########
    #transpose array so each band is a column
    tranBPixels = np.transpose(brightPixels)
    
    a=len(tranBPixels[1])-1
    
    #insert the plot numbers in the first column
    tranBPixels=np.insert(tranBPixels, 0, int(plot[4:]), axis=1)

    try:
        finalSpectra #does finalSpectra exist?    
    except NameError:
        finalSpectra=tranBPixels #create array
    else:
        finalSpectra=np.concatenate((finalSpectra,tranBPixels)) #add to array
    #clear out tranBPixels
    del tranBPixels
    

    ########### end export CSV for convolution ###########
    
    #create H5 file that will store the plot level spectra (brightest pixels)
    hFile = h5py.File('data/brightPixelsH5/bri' + plot + '.h5', 'a')  
    #grp = hFile.create_group("Reflectance")
    hFile['Reflectance'] = brightPixels
    H5file.close()
    hFile.close()
 
name=plot[:4]+'spectra.csv'

#export csv
np.savetxt(name, finalSpectra, delimiter=",",fmt='%1.5d')


##################### CLIP CHM to Study Region ##############################
#############################################################################
clippedCHM={}

for plot in plotNamesList:    
    #import chm
    CHM= (r'G:/D17_Data_2014_Distro/02_SJER/SJER_LiDAR_Data/CHM/r_filtered_CHM_pit_free.tif')  
    
    #clipRaster(inputRaster,clipExtent)
    #[leftx, rightx, topy, bottomy]
    #plot vertices was: [left X, Lower Y, right X, Upper Y ]
    #it's now leftx, rightx, topy, bottomy
    extent=[ plotBound[plot][0][0],plotBound[plot][0][1],plotBound[plot][0][2],plotBound[plot][0][3]]
    #return an array representing the clipped CHM
    clippedCHM[plot]=clipRaster(CHM,extent)
     
    #write the CHM out as a geotif
    filenameCHM=('data/chmTiff/' + plot + 'chm.tif' )
    writeGeotiff(filenameCHM,clippedCHM[plot],plotBound[plot][0][0],plotBound[plot][0][2],EPSG=32611)

####################### END CLIP CHM #######################################
############################################################################

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
NDNI={}

for file in briPixH5Files:
    plotName = file[3:-3]
    print plotName
    filePath =(briPixH5Path + file) 
    #open the h5 file     
    H5file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode
    
    #Select the reflectance dataset within the flightline 
    reflectance=H5file['/Reflectance']
    b1=(reflectance[224,:]).astype('float')
    b2=(reflectance[258,:]).astype('float')
    NDNI[plotName]=((1/np.log(b1))-(1/np.log(b2))) / ((1/np.log(b1))+(1/np.log(b2)))

    

print ("NDNI calculated")

















####################################
#OPTIONAL - quick plot to test that this is working!!
#####################################

#turn all of the lists into one list of numbers to plot a histogram of the data.
import itertools
list2d = plotReflectance
merged = list(itertools.chain.from_iterable(list2d))


from matplotlib import pyplot as plt
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
	