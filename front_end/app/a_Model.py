# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:29:31 2015

@author: ryan
"""

import matplotlib.pyplot as plt
import numpy as np

def modelit(fromUser  = 'Default', population = 0):
    print 'The population is %i' % population
    result = population/1000000.0
    if fromUser != 'Default':
        return result
    else:
        return 'check your input'

def graph_prices(time_stamps, iprices,fprices,gname):
    
    x = np.arange(1,10)

    