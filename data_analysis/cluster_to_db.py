# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 13:25:55 2015

@author: ryan
"""

import os
from pprint import pprint as pp
import pandas as pd
import json
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import itertools
import copy
import seaborn as sns
import pymysql as mdb

from sqlalchemy import create_engine
from sqlalchemy.types import String


df = pd.read_pickle('df_price_cluster.pkl')

engine = create_engine("mysql+pymysql://root:hats@localhost/ssf_db", echo=False)
df.to_sql(name='cluster_price', con=engine, if_exists = 'append', index=True)