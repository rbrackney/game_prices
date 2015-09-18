# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:29:31 2015

@author: ryan
"""

import matplotlib.pyplot as plt
import numpy as np
import datetime
import StringIO
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
#from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
from flask import make_response

def modelit(fromUser  = 'Default', population = 0):
    print 'The population is %i' % population
    result = population/1000000.0
    if fromUser != 'Default':
        return result
    else:
        return 'check your input'

def graph_prices(x, y, gname):
    fig=Figure(facecolor='white')
    ax=fig.add_subplot(111)
    #now=datetime.datetime.now()
    #delta=datetime.timedelta(days=1)
    #for i in range(10):
    #    x.append(now)
    #    now+=delta
    #    y.append(random.randint(0, 1000))
    #ax.plot_date(x, y, '-')
    ax.plot(x,y,'r-')
    #ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    
    ax.set_ylim([0,np.max(y) + np.max(y) * 0.10])
    ax.set_xlabel('Time')
    #ax.set_axis_bgcolor('red')

    formatter = FuncFormatter(money_format)
    ax.yaxis.set_major_formatter(formatter)
    fig.autofmt_xdate()
    
    
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
    
def money_format(x, pos):
    'The two args are the value and tick position'
    return '$%1.2f' % (x)
