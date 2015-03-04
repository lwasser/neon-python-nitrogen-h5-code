# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 15:50:34 2015

@author: lwasser
"""

a = np.empty([2,5])
b = np.append(a,np.zeros([len(a),1]),1)


try:
    dog
    #does dog exist
    
except NameError:
    dog=np.array
else:
    print 'yes'
    
    
    a = np.array([[1, 1], [2, 2], [3, 3]])
    np.insert(a, 0, 5, axis=1)
