# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 19:58:37 2014
This code plots a shapefile
@author: law
"""



#   -- import --
import shapefile
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from pylab import imshow, show, get_cmap
#from array import array

#   -- input --
sf = shapefile.Reader("data/sjerPlots/new_shapefile.shp")
recs    = sf.records()
shapes  = sf.shapes()
Nshp    = len(shapes)
cns     = []
for nshp in xrange(Nshp):
    cns.append(recs[nshp][0])
#cns = array(cns)
cm    = get_cmap('Dark2')
cccol = cm(1.*arange(Nshp)/Nshp)
#   -- plot --
fig     = plt.figure()
ax      = fig.add_subplot(111)
for nshp in xrange(Nshp):
    ptchs   = []
    pts     = array(shapes[nshp].points)
    prt     = shapes[nshp].parts
    par     = list(prt) + [pts.shape[0]]
    for pij in xrange(len(prt)):
     ptchs.append(Polygon(pts[par[pij]:par[pij+1]]))
    ax.add_collection(PatchCollection(ptchs,facecolor=cccol[nshp,:],edgecolor='k', linewidths=.1))
ax.set_xlim(-180,+180)
ax.set_ylim(-90,90)
fig.savefig('test.png')



##########
##########
from fiona import collection
#curl https://bootstrap.pypa.io/ez_setup.py | python
#fiona has several dependencies including six and argparse.
#also ran into erros and had to reinstall setuptools...
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from matplotlib.collections import PatchCollection
from itertools import imap
from matplotlib.cm import get_cmap

cm = get_cmap('Dark2')

figure, axes = plt.subplots(1)

source_path = "data/sjerPlots/new_shapefile.shp"

with collection(source_path, 'r') as source:
    patches = imap(PolygonPatch, (record['geometry'] for record in source)

axes.add_collection( PatchCollection ( patches, cmap=cm, linewidths=0.1 ) )

axes.set_xlim(-180,+180)
axes.set_ylim(-90,90)

plt.show()