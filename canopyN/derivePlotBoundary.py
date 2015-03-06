# -*- coding: utf-8 -*-
"""
Created on Fri Mar 06 12:43:14 2015

@author: lwasser
"""

def derivePlotBoundary(centerx, centery, widthx, heighty):
    '''
    This function will take an xy plot centroid and will derive the four corner
    boundaries using the x and y dimensions of the plot
    inputs
    centerx, centery - this is the xy centroid of the plot
    widthx and heighty - this is the length of the plot
    Returns a list of coordinates leftx, rightx, topy, bottomy
    '''
    # derive plot edges from centroid xy
    lx=float(centerx)-(widthx/2)
    rx=float(centerx)+(widthx/2)
    #top and bottom y
    ty=float(centery)+(heighty/2)
    by=float(centery)-(heighty/2)
    #return the values as a list
    return [lx,rx,ty,by]
