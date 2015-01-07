# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 16:57:31 2014

@author: law
"""
import numpy as np
import os

from matplotlib import pyplot as plt

os.chdir('/Users/law/Documents/GitHub_Lwasser/2015-01-05-wise-cuboulder/novice/python')

data=np.loadtxt(fname='inflammation-01.csv', delimiter=',')

plt.imshow(data)
plt.show()

ave_inflammation = data.mean(axis=0)
plt.plot(ave_inflammation)
plt.show()

print 'maximum inflammation per day'
plt.plot(data.max(axis=0))
plt.show()

print 'minimum inflammation per day'
pyplot.plot(data.min(axis=0))
pyplot.show()

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal')
ax.plot(data.std(axis=0))
plt.ylabel('UTM Y')
plt.xlabel('UTM X')
plt.xlim([0, 40])
plt.ylim([0, 6])



plt.figure(figsize=(10.0, 3.0))

plt.subplot(311)
plt.ylabel('average')
plt.plot(data.mean(0))

plt.subplot(312)
plt.ylabel('max')
plt.plot(data.max(0))

plt.subplot(313)
plt.ylabel('min')
plt.plot(data.min(0))

plt.tight_layout()
plt.show()


##################
#Functions
#################

def addstuff(num1,num2):
	return num1+num2


def fahr_to_kelvin(temp):
    return ((temp - 32) * (5/9)) + 273.15
				
def fence(word1,word2):
	return word1+word2+word1
	

def endLetters(word):
     return word[0]+word[-1]
					
					
				

###
#lessone 3


from ipythonblocks import ImageGrid
grid = ImageGrid(5, 3,fill=(255,255,255),block_size=2000)
grid.show()


ImageGrid(5,5,lines_on=False)

ImageGrid(5,3,fill=255,255,255)

ImageGrid()
row = ImageGrid(8, 1)
row[0, 0] = (0, 0, 0)   # no color => black
row[1, 0] = (255, 255, 255) # all colors => white
row[2, 0] = (255, 0, 0) # all red
row[3, 0] = (0, 255, 0) # all green
row[4, 0] = (0, 0, 255) # all blue
row[5, 0] = (255, 255, 0) # red and green
row[6, 0] = (255, 0, 255) # red and blue
row[7, 0] = (0, 255, 255) # green and blue
row.show()

from ipythonblocks import show_color
show_color(214, 90, 127)

from ipythonblocks import colors
c = ImageGrid(3, 2)
c[0, 0] = colors['Fuchsia']
c[0, 1] = colors['Salmon']
c[1, 0] = colors['Orchid']
c[1, 1] = colors['Lavender']
c[2, 0] = colors['LimeGreen']
c[2, 1] = colors['HotPink']
c.show()
