''' This script was created to fill voids in the ASTER GDEM2 portion of the global 90m DEM through the delta surface fill method. Input data for this method include: 

           Tiles from the global 90m DEM with voids (at N60 and above and derived from ASTER GDEM2 source data)
           Corresponding tiles from the GLSDEM dataset

All tiles are in 10 by 11.5 degree extents, in order to cover the void-prone portion of the global dataset using tiles that are of reasonable size for processing.

This script performs the following procedures:
       1) Clip tiles from global DEM:10 degrees wide by 11.5 degrees high
       2) Import global DEM and corresponding GLSDEM tile for each extent, convert to array
       3) Create delta surface (with voids that are native to global DEM): DSwithVoids= GLSDEM - global DEM
       4) Calculate mean of delta surface with voids (negating 'nodata' values)
       5) Insert mean into center of 11 x 11 pixel voids 
       6) Write to raster and run gdal_translate to set null
       7) In GRASS, run spline interpolation (-r.fillnulls, with tension=135, smoothing= 0.6) on raster from step 6
       8) Import interpolated delta surface, convert to array
       9) Obtain estimated DEM values:  EstimatedGlobalDEM= GLSDEM - InterpolatedDeltaSurface
       10) Create final DEM by replacing void pixels in global DEM with values obtained in step 9
       11) Write to raster and run gdal_translate to set null value

Created by: Natalie Robinson, September 2012
'''

import os
import sys
import re
import string
import osgeo
from osgeo import gdal
from osgeo.gdalconst import *
import subprocess
from subprocess import *
import numpy as np
import osr

#Set functions:---------------------------------------------------------------------------------------------
def CreateArs(GLSRas,GlobRas):
     '''Convert input rasters to arrays'''
     global colsGlob #Create global variables: ea. array, # rows/cols (for other array creation)
     global rowsGlob
     global GLSAr  
     global GlobAr
     global RasGlob
     RasGLS=gdal.Open(GLSRas,GA_ReadOnly)
     RasGlob=gdal.Open(GlobRas,GA_ReadOnly)
     colsGlob=RasGlob.RasterXSize
     rowsGlob=RasGlob.RasterYSize
     GLSAr=RasGLS.ReadAsArray(0,0,colsGlob,rowsGlob)
     GlobAr=RasGlob.ReadAsArray(0,0,colsGlob,rowsGlob)


def WriteRaster (raster,dst_filename,ncol,nrow,array):
        '''Create raster from array. This needs to be followed by gdal_translate command to set null value (I cannot get dataset.SetNoDataValue() to work)'''
        driver = raster.GetDriver()
        dst_ds = driver.Create(dst_filename, ncol, nrow,1,gdal.GDT_Int16)
        dst_ds.SetGeoTransform(raster.GetGeoTransform())
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326) #WGS84 lat long.
        dst_ds.SetProjection( srs.ExportToWkt() )
        dst_ds.GetRasterBand(1).WriteArray(array)
        format = 'EHdr'
        driver = gdal.GetDriverByName(format)
        dst_ds_new = driver.CreateCopy(dst_filename, dst_ds)
        dst_ds = None


def NullCheck(InFile):
       '''Check global DEM tiles to see if they contain null values (only run the rest of the script on those that do).
       1) Convert input raster to array, 2) check for null values'''
    Raster=gdal.Open(InFile,GA_ReadOnly)
    cols=Raster.RasterXSize
    rows=Raster.RasterYSize
    Array=Raster.ReadAsArray(0,0,cols,rows)
    if Array.min()== -32768:
        print InFile

def CreateInterpDS(DeltSurfAr):
       '''Calculate mean of delta surface (negating voids and as integer value), and insert into ctr. of 11 x 11 pixel voids'''
       DeltSurfFlat=DeltSurfAr.flatten()
       DeltSurfFlat=DeltSurfFlat[DeltSurfFlat != -32768]  
       MnDeltSurf= round(DeltSurfFlat.mean(),0)  
       print MnDeltSurf
       global DSCtrFillAr
       DSCtrFillAr=DeltSurfAr.copy()
       for i in range(5,DeltSurfAr.shape[0]-5):
           for j in range(5,DeltSurfAr.shape[1]-5):
               if np.mean(DSCtrFillAr[i-5:i+6,j-5:j+6])==-32768:
                   DSCtrFillAr[i,j]=MnDeltSurf


def ProcessInGRASS(OutPath,filename):
    '''For input files: 
           1) import file to GRASS, in location/mapset that encompasses all files to be processed
           2) Reset region to match boundaries of file
           3) Run spline interpolation to fill voids at tension=135, smoothing=0.6
           4) export output (this causes loop to fail...)
     '''
     gs.run_command('r.in.gdal', input=OutPath+'/'+filename, output=filename[0:6]+filename[14:-4])
     gs.run_command('g.region', rast=filename[0:6]+filename[14:-4])
     print 'You are on tile: ', gs.region()
     gs.run_command('r.fillnulls', input=filename[0:6]+filename[14:-4], output='DSInterp_'+filename[3:6]+filename[-13:-9], tension=135, smooth=0.6, method='rst')
     #gs.run_command('r.gdal.out', input='DSInterp_'+filename[3:6]+'_'+filename[14:-4]+'_T135S0S0pt6', format='EHdr', type='Int16', output=OutPath+'/'+filename[0:2]+'Filled'+filename[2:-4]+'.bil', nodata=-32768)


def CreateFinalDEM(Raster_interp,Raster_GLS,Raster_Glob,DestPath):
      '''For each tile: 
      1) Import void-filled delta surface and corresponding GLS and global datasets- open as arrays
      2) subtract void-filled delta surface from GLS
      3) create final array where values = global DEM for non-void cells. GLS - interpolatled values for void cells
      4) create ouput raster
      '''
      InterpDS=Raster_interp
      InterpDSRas=gdal.Open(InterpDS,GA_ReadOnly)
      cols= InterpDSRas.RasterXSize
      rows=InterpDSRas.RasterYSize
      InterpDSAr=InterpDSRas.ReadAsArray(0,0,cols,rows)
      GLSMatch=Raster_GLS
      GLSMatchRas=gdal.Open(GLSMatch,GA_ReadOnly)
      GLSMatchAr=GLSMatchRas.ReadAsArray(0,0,cols,rows)
      GlobMatch=Raster_Glob
      GlobMatchRas=gdal.Open(GlobMatch,GA_ReadOnly)
      GlobMatchAr=GlobMatchRas.ReadAsArray(0,0,cols,rows)
      DSF_Ar=GLSMatchAr-InterpDSAr  #Subtract interpolated surface from GLS dataset
      FinalDEM=np.where(GlobMatchAr==-32768,DSF_Ar,GlobMatchAr)  #Insert DSF-filled pixels into void in final DEM
      WriteRaster(GlobMatchRas,DestPath+'VoidFilled_'+Raster_interp[-33:-13]+'.bil',cols,rows,FinalDEM)


#Set paths for various parts of script---------------------------------------------------------------------
InGlobal="/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60_83_WholeGlobe.bil"
outDir="/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/"
sourceDir = '/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2'
OutPath='/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters'
DestPath='/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/FilledDEMs/'

###********************************************************************************************
#1) Clip tiles from global DEM:10 degrees wide by 11.5 degrees high
#Define filenames, beginning & end lat/lon to be fed into clip function
FnameEast=[]
for i in range(0,180,10):
   for j in [60.0,71.5]:
      FnameEast.append(outDir+"GDEM2_N"+str(j)+"to"+str(j+11.5)+"E"+str(i)+"to"+str(i+10)+".bil")


FnameWest=[]
for i in range(180,0,-10):
   for j in [60.0,71.5]:
         FnameWest.append(outDir+"GDEM2_N"+str(j)+"to"+str(j+11.5)+"W"+str(i)+"to"+str(i-10)+".bil")


#Put 0 before double digit, and 00 before single digit longitudes for correct file naming
for i in range (0,len(FnameEast)):
    '''Correct western longitude'''
    if FnameEast[i][-7]=='o':
        FnameEast[i]=FnameEast[i][0:-6]+'0'+FnameEast[i][-6:]
    if FnameWest[i][-6]=='o':
        FnameWest[i]=FnameWest[i][0:-5]+'00'+FnameWest[i][-5:]
    if FnameWest[i][-7]=='o':
        FnameWest[i]=FnameWest[i][0:-6]+'0'+FnameWest[i][-6:]


for i in range (0, len(FnameEast)):
    '''Correct eastern longitude'''
    if FnameEast[i][-12]=='E':
        FnameEast[i]=FnameEast[i][0:-11]+'0'+FnameEast[i][-11:]
    if FnameEast[i][-11]=='E':
        FnameEast[i]=FnameEast[i][0:-10]+'00'+FnameEast[i][-10:]
    if FnameWest[i][-12]=='W':
        FnameWest[i]=FnameWest[i][0:-11]+'0'+FnameWest[i][-11:]


#Define input and output longitudes for each file
i=0
ILE= -0
OLE=10
ILW= -180
OLW= -170
InLonEast=[];OutLonEast=[];InLonWest=[];OutLonWest=[]

while (i< 18):
   InLonEast.append([ILE]*2)
   OutLonEast.append([OLE]*2)
   InLonWest.append([ILW]*2)
   OutLonWest.append([OLW]*2)
   ILE= ILE+10;OLE=OLE+10;ILW=ILW+10;OLW=OLW+10
   i= i+1


#create lists of input and output latitudes and longitudes
InLat=[60.0,71.5]*18
OutLat=[71.5,83.0]*18

InLonEast=[j for i in InLonEast for j in i]
OutLonEast=[j for i in OutLonEast for j in i]
InLonWest=[j for i in InLonWest for j in i]
OutLonWest=[j for i in OutLonWest for j in i]

#Convert to string for input in subprocess call
for i in range (0,len (InLonEast)):
   InLonEast[i]= "%.7f" % (InLonEast[i])
   OutLonEast[i]= "%.7f" % (OutLonEast[i])
   InLonWest[i]= "%.7f" % (InLonWest[i])
   OutLonWest[i]= "%.7f" % (OutLonWest[i])
   InLat[i]="%.7f" % (InLat[i])
   OutLat[i]="%.7f" % (OutLat[i])
   

##Clip files 
for i in range (0,len(FnameEast)):
    subprocess.call (['gdalwarp','-te',InLonEast[i],InLat[i],OutLonEast[i],OutLat[i],'-ot','Int16','-r','bilinear','-srcnodata','-32768','-dstnodata','-32768','-of','EHdr',InGlobal, FnameEast[i]])


for i in range (0,len(FnameWest)):
    subprocess.call (['gdalwarp','-te',InLonWest[i],InLat[i],OutLonWest[i],OutLat[i],'-ot','Int16','-r', 'bilinear','-srcnodata','-32768','-dstnodata','-32768','-of','EHdr',InGlobal, FnameWest[i]])

#***********************************************************************************************************************************
#2) Import global DEM and corresponding GLSDEM tile for each extent where global DEM contains voids, convert to array

# Get file names and check for voids
InFile=[]
for dirname, dirnames, filenames in os.walk(sourceDir):
    for filename in filenames:
        ext = os.path.splitext(filename)[1]
        if ext == ".bil":
            InFile.append(sourceDir+'/'+filename)
 

for j in range(0,len(InFile)):
    NullCheck(InFile[j])


#List files containing nulls--------------------------------------------------------------------------------
GLS_East=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E000to010.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E010to020.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E020to030.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E030to040.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E040to050.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E050to060.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E060to070.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E070to080.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E080to090.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E090to100.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E100to110.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E110to120.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E120to130.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E130to140.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E140to150.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E150to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E160to170.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5E170to180.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E010to020.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E020to030.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E030to040.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E040to050.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E050to060.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E060to070.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E070to080.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E080to090.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E090to100.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E100to110.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E110to120.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E120to130.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E130to140.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E140to150.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E150to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0E170to180.bil']

Global_East=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E000to010.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E010to020.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E020to030.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E030to040.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E040to050.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E050to060.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E060to070.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E070to080.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E080to090.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E090to100.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E100to110.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E110to120.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E120to130.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E130to140.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E140to150.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E150to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E160to170.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5E170to180.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E010to020.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E020to030.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E030to040.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E040to050.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E050to060.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E060to070.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E070to080.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E080to090.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E090to100.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E100to110.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E110to120.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E120to130.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E130to140.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E140to150.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E150to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0E170to180.bil']

GLS_West=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5W180to170.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N60.0to71.5W170to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/GLSDEM_N60AndAbove/MergedTiles/GLSDEM_N71.5to83.0W180to170.bil']
            
Global_West=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5W180to170.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N60.0to71.5W170to160.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/InDEM_AsterGdem2/GDEM2_N71.5to83.0W180to170.bil']

#***************************************************************************************************
# Create delta surface [steps 3) to 6)]  (with voids that are native to global DEM): DSwithVoids= GLSDEM - global DEM
#Create output filenames
for i in range(0,len(Global_East)):
    if Global_East[i][-24:]==GLS_East[i][-24:]:
        CreateArs(GLS_East[i],Global_East[i])
        DSWithVoidsAr= np.where(GlobAr==-32768,-32768,GLSAr-GlobAr)
        CreateInterpDS(DSWithVoidsAr)
        WriteRaster(RasGlob,OutPath+'/DeltSurf_'+Global_East[i][-24:],colsGlob,rowsGlob,DSCtrFillAr)    


for i in range(0,len(Global_West)):
    if Global_West[i][-24:]==GLS_West[i][-24:]:
        CreateArs(GLS_West[i],Global_West[i])
        DSWithVoidsAr= np.where(GlobAr==-32768,-32768,GLSAr-GlobAr)
        CreateInterpDS(DSWithVoidsAr)
        WriteRaster(RasGlob,OutPath+'/DeltSurf_'+Global_West[i][-24:],colsGlob,rowsGlob,DSCtrFillAr)   


#Gdal_translate to set nodata value
for dirname, dirnames, filenames in os.walk(OutPath):
    for filename in filenames:
        ext = os.path.splitext(filename)[1]
        if filename[0:5]=='Delt' and ext == ".bil":
            subprocess.call(['gdal_translate','-ot','Int16','-of','EHdr','-a_nodata','-32768',OutPath+'/'+filename,OutPath+'/DS_'+filename[-24:]])

#******************************************************************************************
#7) In GRASS, run spline interpolation (-r.fillnulls, with tension=135, smoothing= 0.6) on raster from step 6

# **From terminal:
grass70 
ipython 

import grass.script as gs
import os

#Set location and mapset
location = '/Global_N60AndUp'
mapset = 'Global_N60AndUp'
gs.run_command('g.gisenv', set='LOCATION_NAME=%s' % location)
gs.run_command('g.gisenv', set='MAPSET=%s' % mapset)

#Check that the location/mapset are correct:
gs.gisenv()

#Loop through delta surfaces and process each in GRASS
for dirname, dirnames, filenames in os.walk(OutPath):
   for filename in filenames:
        ext = os.path.splitext(filename)[1]
        if filename[0:5]=='DS_N6' and ext == ".bil" or filename[0:5]=='DS_N7' and ext == ".bil":
            ProcessInGRASS(OutPath,filename)


# *Export GRASS rasters using -r.gdal.out commands from GRASS
#Script= /home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/RGdalOutCommands_InterpolatedDS

#*********************************************************************************************
#Create final DEM [steps 8) to 11)]       
#List names of interpolated files for input to final processing
DSInterpFileEast=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E000to010_T135S0.6.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E010to020_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E020to030_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E030to040_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E040to050_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E050to060_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E060to070_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E070to080_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E080to090_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E090to100_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E100to110_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E110to120_T135S0.6.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E120to130_T135S0.6.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E130to140_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E140to150_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E150to160_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E160to170_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5E170to180_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E010to020_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E020to030_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E030to040_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E040to050_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E050to060_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E060to070_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E070to080_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E080to090_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E090to100_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E100to110_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E110to120_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E120to130_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E130to140_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E140to150_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E150to160_T135S0.6.bil', 
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0E170to180_T135S0.6.bil']

DSInterpFileWest=['/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5W180to170_T135S0.6.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N60.0to71.5W170to160_T135S0.6.bil',
'/home/robinson/Desktop/GlobalDEM_FinalProcessing/DeltSurfFill/DeltaSurfRasters/DSInterp_N71.5to83.0W180to170_T135S0.6.bil']


#For matching extents: 1)load interpolated delta surface, GLSDEM and global 90m DEM, 2) create output DEM by replacing void values with GLSDEM-InterpoltedDeltaSurface.
for i in range (0,len(GLS_West)):
      if GLS_West[i][-24:-4]==DSInterpFileWest[i][-33:-13]==Global_West[i][-24:-4]:
          CreateFinalDEM(DSInterpFileWest[i],GLS_West[i],Global_West[i],DestPath)
          

for i in range (0,len(GLS_East)):
      if GLS_East[i][-24:-4]==DSInterpFileEast[i][-33:-13]==Global_East[i][-24:-4]:
          CreateFinalDEM(DSInterpFileEast[i],GLS_East[i],Global_East[i],DestPath)




