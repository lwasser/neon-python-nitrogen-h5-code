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

#external hard drive - mac
#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')

#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')
fileDirectory = (r'F:/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')


#get a list of all files in the directory
from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir(fileDirectory) if isfile(join(fileDirectory,f)) ]

#Generate a list of the names of H5 files in the specified directory
onlyH5files=[]
for f in onlyfiles:
  if f.endswith(".h5"):
    onlyH5files.append(f)
    
#should be able to populate this ahead of time with Nan
#oop through all of the files in the directory, extract flightline bounds and resolution
#calculate extent in UTM
finalLookup=[]   
#for f in onlyH5files:
    #iterate through all H5 files in the directory
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

#plotBoundariesPath=(r'F:\ESA_WorkshopData\WorkingDirectory\Field_SHP_Use\SJERPlotCentroids_Buff_Square.shp')
#for mac
#plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
plotBoundariesPath=(r'C:/Users/lwasser/Documents/GitHub/adventures-with-python/data/sjerPlots/SJERPlotCentroids_Buff_Square.shp')

#read shapefile data
sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()

#read all of the fields in the shapefile
plotMetadata=sf.fields
records = sf.records()
#Create dictionary object that will store final data
#to access attribute data records[0][2:3]
plotIdDict={}


#loop through all plots
#find the flightlines that completely overlap (intersect) the with the plot boundary
#note: there could be an intersect command - look into that.

#create a disctionary of plot boundary coordinates
plotBound={}

for j in xrange(len(shapes)):
    #get the coordinates of the plot boundary
    #bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
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
            #print(plotVertices[0], 'should be bigger than', finalLookup[i][3])
            #print(plotVertices[2], 'should be smaller than', finalLookup[i][4])										
            #print(plotVertices[1], 'should be bigger than', finalLookup[i][2])
            #print(plotVertices[3], 'should be smaller than', finalLookup[i][1])										

            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4],finalLookup[i][6],finalLookup[i][7]])
            #would like to figure out how to use the code below but it makes too many lists
		 #isInTemp.append([i,finalLookup[i][0:4]])
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

spectraDict={}
for keys in disDict:
#for char in 'a':
    print(keys)
    #create empty H5 File - this is where all of the plot data will be stored
    hFile = h5py.File('data/h5/Plot' + keys + '.h5', 'a')  
    #get the flightline that needs to be subsetted
    
    #filePath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/' 
    #			+ disDict[keys][1])

    filePath =(fileDirectory + disDict[keys][1])    
    file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode

    #Select the reflectance dataset within the flightline 
    reflectance=file['/Reflectance']

    #get flightline ID	
    flID=	int(disDict[keys][0])	
    # Grab the lower left corner of the flightline from the original flightline lookup table
    flLowerCorner= [finalLookup[flID][3],finalLookup[flID][1]]
    
    #i need to grab the plot boundary somewhere
    
    # Define / Calculate subset reflectance data from the flightline based upon plot boundary			
    SubsetCoordinates=[int(plotBound[keys][0]-flLowerCorner[0]),int(plotBound[keys][2]-flLowerCorner[0]),
                       int(flLowerCorner[1]-plotBound[keys][3]),int(flLowerCorner[1]-plotBound[keys][1])]
			
        
    #Define the final slice from the flightline
    # need to round the above so it's integers instead of floating point.
    # note that the data are wavelength, columns? rows <<- double check this
       
    plotReflectance=reflectance[54,SubsetCoordinates[2]:SubsetCoordinates[3],SubsetCoordinates[0]:SubsetCoordinates[1]]   
    spectraDict[keys] =  plotReflectance
    
    #grp = hFile.create_group("Reflectance")
    hFile['Reflectance'] = plotReflectance
    file.close()
    hFile.close()
#quick plot to test that this is working!!

#turn all of the lists into one list of numbers to plot a histogram of the data.
import itertools
list2d = plotReflectance
merged = list(itertools.chain.from_iterable(list2d))
plt.hist(merged)
plt.title("Histogram")
plt.xlabel("Reflectance")
plt.ylabel("Frequency")

#render a quick image
plt.imshow(plotReflectance_Sub)
    

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
	








########################################################################
<<<<<<< HEAD
#Plot Flightlines and Field Site  boundary 
=======
#plot things
>>>>>>> FETCH_HEAD
########################################################################

import matplotlib
import matplotlib.pyplot as plt

onePlot=plotIdDict['SJER1068'][0]

#create the figure
fig = plt.figure()
ax = fig.add_subplot(111)

#this code is a bit cumbersome.. figured out another way.
for i in xrange(len(onePlot)): 
    print(i)
    xWidth=(onePlot[i][5]-onePlot[i][4])
    yHeight=(onePlot[i][2]-onePlot[i][3])
    locals()["rect"+str(i)] = matplotlib.patches.Rectangle((onePlot[i][4],onePlot[i][3]), xWidth, yHeight, fill=None, edgecolor='red')
    ax.add_patch(locals()["rect"+str(i)])
    #ax.add_patch(matplotlib.patches.Rectangle((onePlot[i][4],onePlot[i][2]), xWidth, yHeight, edgecolor='violet'))

<<<<<<< HEAD

#add plot boundary
#bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
plotVertices=shapes[0].bbox 
plotBoundary = matplotlib.patches.Rectangle((plotVertices[0],plotVertices[1]), 40, 40, edgecolor='blue', facecolor='white')
ax.add_patch(plotBoundary)  

plt.ylabel('UTM Y')
plt.xlabel('UTM X')
#make sure plot name is on the 
#plt.title('NEON AOP flightlines for plot ' + plotNamesList[2])
plt.xlim([250000, 265000])
plt.ylim([4104000, 4115000])

plt.show()










#############################
#use this code to sort out the smallest values...
dis=[[200, 451], [30, 5], [20, 120]]
min(dis, key=lambda item: (item[0], item[1]))

dis.index(min(dis, key=lambda item: (item[0], item[1])))



##################
#Code to calculate the closest point
########################

recCen=[[100,400],[140,450],[150,500]]
plotcent=[170,620]
dis=[]
for q in xrange(3):
	dis.append([abs(plotcent[0]-recCen[q][0]),abs(plotcent[1]-recCen[q][1])])





###################################
# extra code
###################################

=======
###################
#dummy test code...
>>>>>>> FETCH_HEAD
recCen=[[100,400],[140,450],[150,500]]
plotcent=[170,620]
dis=[]
for q in xrange(3):
	dis.append([abs(plotcent[0]-recCen[q][0]),abs(plotcent[1]-recCen[q][1])])
	
	
#############################
#use this code to sort out the smallest values...
dis=[[20, 1], [30, 5], [20, 120]]
min(dis, key=lambda item: (item[0], item[1]))

dis.index(min(dis, key=lambda item: (item[0], item[1])))
#############################


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
rect1 = matplotlib.patches.Rectangle((0,0), 200, 800, fill=None, edgecolor='red')
rect2 = matplotlib.patches.Rectangle((100,150), 180, 750, fill=None, edgecolor='green')
rect3 = matplotlib.patches.Rectangle((50,100), 200, 800, fill=None, edgecolor='violet')
plot = matplotlib.patches.Rectangle((150,600), 40, 40, color='blue')

#circle1 = matplotlib.patches.Circle((-200,-250), radius=90, color='#EB70AA')
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_patch(rect3)
ax.add_patch(plot)

#ax.add_patch(circle1)
plt.xlim([-100, 1000])
plt.ylim([-100, 1000])
plt.show()