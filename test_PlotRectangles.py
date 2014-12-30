# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 11:53:37 2014

@author: lwasser
"""

import matplotlib.colorbar as cbar
import pylab as pl
import numpy as np

N = 50
xs = np.random.randint(0, 100, N)
ys = np.random.randint(0, 100, N)
ws = np.random.randint(10, 20, N)
hs = np.random.randint(10, 20, N)
vs = np.random.randn(N)

normal = pl.normalize(vs.min(), vs.max())
colors = pl.cm.jet(normal(vs))


ax = pl.subplot(111)
#for x,y,w,h,c in zip(xs,ys,ws,hs,colors):
#    rect = pl.Rectangle((x,y),w,h,color=c)
#    ax.add_patch(rect)
    
    
#fig = pl.figure()
ax = pl.subplot(111)
onePlot=plotIdDict['SJER1068'][0] 

# Add flightlines which the plot overlaps
for i in xrange(len(onePlot)): 
    print(i)
    xWidth=(onePlot[i][5]-onePlot[i][4])
    yHeight=(onePlot[i][2]-onePlot[i][3])
    rect = pl.Rectangle((onePlot[i][4],onePlot[i][3],onePlot[i][4],onePlot[i][3]),xWidth,yHeight,edgecolor="black",facecolor="none")
    #add patch to data    
    ax.add_patch(rect)
    
    
# Plot the plot boundary
plotVertices=shapes[0].bbox 
plotBoundary = pl.Rectangle((plotVertices[0],plotVertices[1]), 40, 40, edgecolor='blue', facecolor='blue')
ax.add_patch(plotBoundary)  
    
    
ax.set_xlim(250000,265000)
ax.set_ylim(4104000,4115000)
pl.show()

#list all keys in dictionary
#D2.keys()
#let's try to loop through my data

#rect=pl.Rectangle((x,y),w,h)    


#cax, _ = cbar.make_axes(ax) 
#cb2 = cbar.ColorbarBase(cax, cmap=pl.cm.jet,norm=normal) 

#plt.xlim([250000, 265000])
#plt.ylim([4104000, 4115000])


#what is the length of an object?

 len(plotIdDict)
#get list of keys for the dictionary 
 a=plotIdDict.keys()
 #call the dictionary
 plotIdDict[a[1]]


