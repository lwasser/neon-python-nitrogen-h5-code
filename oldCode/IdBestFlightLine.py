# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 16:47:42 2014

@author: lwasser
"""
import matplotlib
import matplotlib.pyplot as plt

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