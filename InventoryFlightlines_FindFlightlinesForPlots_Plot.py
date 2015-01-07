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
<<<<<<< HEAD
#external hard drive - mac
fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')
=======
#fileDirectory = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
#fileDirectory = (r'X:/All_data_distro/D17/SJER/2013/SJER_Spectrometer_Data/2013061320/Reflectance')
fileDirectory = (r'F:/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/')
>>>>>>> FETCH_HEAD


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
plotBoundariesPath=(r'/Volumes/My Passport/ESA_WorkshopData/WorkingDirectory/Field_SHP_Use/SJERPlotCentroids_Buff_Square.shp')
#plotBoundariesPath=(r'C:/Users/lwasser/Documents/GitHub/adventures-with-python/data/sjerPlots/SJERPlotCentroids_Buff_Square.shp')


sf = shapefile.Reader(plotBoundariesPath)
shapes = sf.shapes()



#read all of the fields in the shapefile
plotMetadata=sf.fields
records = sf.records()
#Create dictionary object that will store final data
#to access attribute data records[0][2:3]
plotIdDict={}

<<<<<<< HEAD
#loop through all plots
#find the flightlines that completely overlap (intersect) the with the plot boundary
#note: there could be an intersect command - look into that.
#for j in xrange(len(shapes)):
for j in xrange(2):
    
=======
#loop through all plots, determine which fligthlines they fall wtihin the boundary of
#add the flightlines that fall wtihin the boundary of each plot to the dictionary
for j in xrange(len(shapes)):
>>>>>>> FETCH_HEAD
    #get the coordinates of the plot boundary
    #bbox saves 4 corners as follows [left X, Lower Y, right X, Upper Y ]
    plotVertices=shapes[j].bbox
    #grab plot centroid coords
    plotCentroidX=float(records[j][3])
    plotCentroidY=float(records[j][2])
    
    #finalLookup order 1:Ytop 2:ybottom 3:xLeft  4:xRIGHT
    #loop through all flightlines - figure out which ones contain the plot boundary
<<<<<<< HEAD
    print(j)
    print(records[j][0])
=======
    #if they create the boundary, then store that in the disctionary  
>>>>>>> FETCH_HEAD
    #plotID
    isInTemp=[]
    for i in xrange(len(finalLookup)):
    #for i in xrange(1):					
        if ((plotVertices[0] > finalLookup[i][3]) and (plotVertices[2] < finalLookup[i][4])) and ((plotVertices[1] > finalLookup[i][2]) and (plotVertices[3] < finalLookup[i][1])):
            #add the flightline index, the extents of the flightline and the plot centroid to the dict
            print(plotVertices[0], 'should be bigger than', finalLookup[i][3])
            print(plotVertices[2], 'should be smaller than', finalLookup[i][4])										
            print(plotVertices[1], 'should be bigger than', finalLookup[i][2])
            print(plotVertices[3], 'should be smaller than', finalLookup[i][1])										

            isInTemp.append([i,finalLookup[i][0],finalLookup[i][1],finalLookup[i][2],finalLookup[i][3],finalLookup[i][4],finalLookup[i][6],finalLookup[i][7]])
            #would like to figure out how to use the code below but it makes too many lists
		 #isInTemp.append([i,finalLookup[i][0:4]])
	   #This dictionary contains two lists. the first list is the flightline extents and the centroid (6 numbers)
	   #the second list is the X,Y lower left hand corner of the plot.		
        plotIdDict[records[j][0]]=[isInTemp,plotVertices]
        

								
								


plotNamesList=plotIdDict.keys()
#syntax to call a particular location inthe dictionary using the 
#plotIdDict[plotNamesList[0]]

#loop through each plot and find the best flightline (closest to the center)

#first -- get plot ID
#then get flightlines for plot
#calculate different between plot center and the flightline center
#calculate min value from all distances
theIndex=0

disDict={}
#loop through all keys or plots in the dictionary
#and find the BEST flightline for each plot

# right now this isn't working... i need to find the point furthest away from the edge
# the way to test this is to extract the values for the first two plots and the associated flightlines... then 
#post to stack overflow.
for keys in plotIdDict:
    dis=[]
    print(keys)	
    for j in xrange(len(plotIdDict[keys][0])):
        print(j)
        #a=plotIdDict[keys]
        #calculate difference between the plot center and the flightline center to
        #identify the closest
        dis.append([plotIdDict[keys][0][j][0],plotIdDict[keys][0][j][1],abs(float(records[theIndex][3])-plotIdDict[keys][0][j][6]),
            abs(float(records[theIndex][2])-plotIdDict[keys][0][j][7])])							
            
    
    #calculate the min distance to ID the best flightline
    min(dis, key=lambda item: (item[2], item[3]))
    #get index of min xy difference value
    ab=dis.index(min(dis, key=lambda item: (item[2], item[3])))
    flightlineIndex=[dis[ab][0],dis[ab][1],plotIdDict[keys][1]]
			
    print(ab)
    #disDict contains the index and name of the flightline, (could remove the name)
    #it also contains the bbox coordinates of the plot
    disDict[keys]=flightlineIndex
    #add flightline index to dictionary
    #plotIdDict[keys].append(flightlineIndex)
    theIndex=theIndex+1


print("Done Inventoring Data & Identifying Needed Flightlines!")

###############################
#need to somehow check that the code above it actually pulling the 
# best flightline. 
# Might want to plot out 23 images??
###############################




####################################
#Finally, pull out subset from spectrometer data!
# yea baby!
###################################

#create empty H5 File - this is where all of the plot data will be stored
plotData = h5py.File('data/SJERPlotReflData8.h5', 'a')  

#i should sort these so it doesn't have to loop through each file and reopen it. 
newdict={}
for keys in disDict:
    print(keys)
    #get the flightline that needs to be subsetted
    filePath = (r'/Volumes/My Passport/D17_Data_2014_Distro/02_SJER/SJER_Spectrometer_Data/2013061320/Reflectance/' 
				+ disDict[keys][1])
    file = h5py.File(filePath, 'r')   # 'r' means that hdf5 file is open in read-only mode

    #Select the reflectance dataset within the flightline 
    reflectance=file['/Reflectance']
				
    # Grab the lower left corner of the flightline from the original flightline lookup table
    flightlineLowerCorner=[finalLookup[disDict[keys][0]][3],finalLookup[disDict[keys][0]][2]]
    
    # Define / Calculate subset reflectance data from the flightline based upon plot boundary			
    SubsetCoordinates=[int(disDict[keys][2][0]-flightlineLowerCorner[0]),int(disDict[keys][2][2]-flightlineLowerCorner[0]),
                       int(disDict[keys][2][1]-flightlineLowerCorner[1]),int(disDict[keys][2][3]-flightlineLowerCorner[1])]
			
    #Define the final slice from the flightline
    # need to round the above so it's integers instead of floating point.
    # note that the data are wavelength, columns? rows <<- double check this
    plotReflectance_Sub=reflectance[54,SubsetCoordinates[2]:SubsetCoordinates[3],SubsetCoordinates[0]:SubsetCoordinates[1]]   

    
    groupName='plot_'+keys
    print(groupName)				
    #check to see if this group already exists
    #if plotData[groupName]:			
	#del plotData[groupName]
    #plotData[groupName] = plotReflectance_Sub
    newdict[groupName]	= plotReflectance_Sub

    #file.close()
    #plotData.close() 

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