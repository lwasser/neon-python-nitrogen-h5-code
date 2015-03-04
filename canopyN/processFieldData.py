# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 11:23:15 2015

This code will import spreadsheets containing FSU vegetation sampling data
It will create summary stats per plot for structure (DBH)
It will also extract average N values per plot and by dom / co dom species per plot

@author: Leah A. Wasser
"""

#set working directory
import os
os.chdir('c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN')
#Identify the Site you wish to query data for
site='SJER'

#Define Field Data Path
plotH5FilePath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/data/h5/'
#fieldDataPath='F:/D17_Data_2014_Distro/06_Field_Data/Sampling_Data/D17_Foliar_Chemistry/'

fieldDataPath='c:/Users/lwasser/Documents/GitHub/pythonWork/canopyN/fieldData/'

import pandas as pd
from pandas import read_csv
import numpy as np

#open the csv file as a pandas dataframe
#note that the data as saved (on a mac??) had issues that were resolved by resaving it
#as a csv in excel on windows. macs apparently add extra characters.
f = open(fieldDataPath + 'D17_2013_foliarChem.csv')
dfChem = read_csv(f, header=0)

g =open(fieldDataPath +'D17_2013_vegStr.csv')
dfStr = read_csv(g,header=0)


#get unique site names
plots=np.unique(dfStr.plotid.ravel())

dfStruc = pd.concat([dfStr['siteid'],dfStr['plotid'], dfStr['taxonid'],dfStr['dbh'],dfStr['stemheight']],axis=1)
#header=0 ensures the first row is the index for each column
#df.side_id also works

#first get the total DBH per plot
byPlot = dfStruc.groupby(['plotid'])
plotDBH=byPlot['dbh'].sum()


#group by plot and then taxon
byPlot_Taxon = dfStruc.groupby(['plotid', 'taxonid'])
byPlot_Taxon['dbh'].describe()
#sum DBH by plot and then taxon
dbhTaxon = byPlot_Taxon['dbh'].sum()

#create a class to store variables of interest
class plotData:
    """a class to store plot data """
    def __init__(self, plotid="", species="", dbh= 0, pctDBH=0):
        pass
    #write out as string
    def __str__(self):
        return self.plotid + "," + self.dbh
        
    

#create dataframe from series
#loop through each plot name and create the data frame
plotList =[]
for plot in plots:
    totalDBH=plotDBH[plot]   
    currentData=dbhTaxon[plot]
 
    
    #get list of taxon in plot    
    #a=dbhTaxon[plot].keys()
    
    for species in currentData.keys():
        #call class
        d=plotData()
        d.plotid = plot
        d.dbh = currentData[species]
        d.species = species
        d.pctDBH = currentData[species] / totalDBH
        list=[plot[0:4],d.plotid,d.species,d.dbh,d.pctDBH]
        plotList.append(list)

finDFStr = pd.DataFrame(plotList, columns=["site","plotid","species","totDBH","pctDBH"])

#make sure things add to 1
checkPct = finDFStr.groupby(['plotid'])
finalcheck=checkPct['pctDBH'].sum()
finalcheck

#select rows from the site of interest
siteOnly=dfChem[dfChem.site_id == site]

#create new dataframe from split cells
d2=pd.DataFrame(siteOnly.unique_ID.str.split('-').tolist(), columns="siteNum stemId".split())
#append new columns to siteOnly dataframe
siteOnly['siteNum'],siteOnly['stemId']=(site+d2['siteNum']),d2['stemId']

#just grab the fields that i need.
newDF=pd.concat([siteOnly['siteNum'], siteOnly['totalN'],siteOnly['species_code'],siteOnly['stemId']],axis=1)
#view the first 5 lines of the DF
newDF.head()

#clear additional dataframe
del d2

#get unique site names
a=np.unique(siteOnly.siteNum.ravel())

#calculate average N per plot
avN={}
x=[]
y=[]
for plots in a:
    plotDf=siteOnly[siteOnly.siteNum == plots]
    avN[plots]=[plotDf.totalN.mean(),NDNI[plots].mean()]
    y.append(plotDf.totalN.mean())
    x.append(NDNI[plots].mean())
    del plotDf
        

from matplotlib import pyplot as plt
x=np.array(x)
y=np.array(y)

plt.plot(x, y, '.')

from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print "r-squared:", r_value**2

# fit with np.polyfit
m, b = np.polyfit(x, y, 1)

plt.plot(x, y, '.')
plt.plot(x, m*x + b, '-')
plt.ylabel('Plot Av Measured Total N',fontsize=15)
plt.xlabel('Plot Av NDNI',fontsize=15)
plt.title('This aint pretty but it aint ugly either', fontsize=20)
plt.xlim(0.025,.032)
plt.ylim(1,2.3)
plt.text(.03, 2.2, r'y=' + str(round(m,2)) + 'x+' + str(round(b,2)))
plt.text(.03, 2.15, r'St Error='+ str(round(std_err,4)) + ', R2=' + str(round((r_value**2),2)))
plt.text(.03, 2.1, r'p-value= '+ str(round(p_value,4)) )


    
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print "r-squared:", r_value**2

    