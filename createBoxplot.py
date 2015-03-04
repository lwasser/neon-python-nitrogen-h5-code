# -*- coding: utf-8 -*-
"""
Created on Tue Mar 03 18:43:34 2015

@author: lwasser
"""

import pandas as pd

df = pd.DataFrame(np.random.rand(12,2), columns=['Apples', 'Oranges'] )

df['Categories'] = pd.Series(list('AAAABBBBCCCC'))

pd.options.display.mpl_style = 'default'

df.boxplot(by='Categories')

newDF=pd.concat([siteOnly['siteNum'], siteOnly['totalN'],siteOnly['species_code']],axis=1)


newDF.boxplot(by='species_code')
newDF.boxplot(by='siteNum')


plt=newDF.boxplot(by='species_code')

#fig = axes[0][0].get_figure()

plt.title("Boxplot of Something")


