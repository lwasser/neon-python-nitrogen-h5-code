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


############################## Process the Chem Data #######################

#select rows from the site of interest
#siteOnly=dfChem[dfChem.site_id == site]

#create new dataframe from split cells
d2=pd.DataFrame(dfChem.unique_ID.str.split('-').tolist(), columns="siteNum stemId".split())
#append new columns to siteOnly dataframe
dfChem['siteNum'],dfChem['stemId']=(dfChem['site_id']+d2['siteNum']),d2['stemId']

#just grab the fields that i need.
plotChemDF=pd.concat([dfChem['siteNum'], dfChem['totalN'],dfChem['species_code'],dfChem['stemId']],axis=1)
#view the first 5 lines of the DF
plotChemDF.head()

#group by plot and then taxon
chemByPlot_Taxon = plotChemDF.groupby(['siteNum', 'species_code'])
#byPlot_Taxon['dbh'].describe() - to write things out
#grab mean totalN value by taxon per plot
nPlotTaxon = chemByPlot_Taxon['totalN'].mean()


################################

#create a class to store variables of interest
class plotData:
    """a class to store plot data """
    def __init__(self, plotid="", species="", dbh= 0, pctDBH=0, pctN=float('NaN')):
        pass
    #write out as string
    def __str__(self):
        return self.plotid + "," + self.dbh
        
#create a class to store variables of interest
class plotChemData:
    """a class to store plot data """
    def __init__(self, plotid="", species="", pctN= 0, pctDBH=0):
        pass
    #write out as string
    def __str__(self):
        return self.plotid + "," + self.dbh 

#create dataframe from series
#loop through each plot name and create the data frame that contains structure
#data for that plot
plotList =[]
for plot in plots:
    n=999
    totalDBH=plotDBH[plot]   
    currentData=dbhTaxon[plot]
    #not all plots have chem data, check to make sure there is plot data here
    if plot in nPlotTaxon.keys():
        currentChemData=nPlotTaxon[plot]
    else:
        print 'missing chem data for plot ' + plot
        n=0
        
 
    
    #get list of taxon in plot    
    #a=dbhTaxon[plot].keys()
    
    for aSpecies in currentData.keys():
        #call class
        d=plotData()
        d.plotid = plot
        d.dbh = currentData[aSpecies]
        d.species = aSpecies
        d.pctDBH = currentData[aSpecies] / totalDBH
        #if there's no plot chem data, then set pctN to NaN
        if n==0:
            d.pctN = float('NaN')
        else:    
            #not all species were sampled for N, make sure that this plot has N data for a given species
            if aSpecies in currentChemData.keys():
                d.pctN = currentChemData[aSpecies]
            else:
                d.pctN = float('NaN')
        
        list=[plot[0:4],d.plotid,d.species,d.dbh,d.pctDBH, d.pctN]
        plotList.append(list)
#right now this isn't returning ALL entries... should be 1593
finDFStr = pd.DataFrame(plotList, columns=["site","plotid","species","totDBH","pctDBH","pctN"])

#make sure things add to 1
checkPct = finDFStr.groupby(['plotid'])
finalcheck=checkPct['pctDBH'].sum()
finalcheck



# finDFStr - this is the structure DF and plotChemDF is the chem structure DF

#get unique species available in the chem data
species=np.unique(plotChemDF.species_code.ravel())
#select just the rows in each plot where there is chem data
chemDataAvail=finDFStr[finDFStr.species.isin(species)]

#clear additional dataframe
del d2

#get unique site names
a=np.unique(siteOnly.siteNum.ravel())

#calculate species level average N
for plots in a:
    plotDf=siteOnly[siteOnly.siteNum == plots]
    

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
plt.title('NDNI vs In Situ Leaf Level Canopy N', fontsize=20)
plt.xlim(0.025,.032)
plt.ylim(1,2.3)
plt.text(.03, 2.2, r'y=' + str(round(m,2)) + 'x+' + str(round(b,2)))
plt.text(.03, 2.15, r'St Error='+ str(round(std_err,4)) + ', R2=' + str(round((r_value**2),2)))
plt.text(.03, 2.1, r'p-value= '+ str(round(p_value,4)) )


    
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print "r-squared:", r_value**2

    