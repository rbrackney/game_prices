# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 17:28:46 2015

@author: ryan
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import itertools
import copy
import seaborn as sns
import pandas as pd
from scipy import stats
from scipy.stats import randint as sp_randint
from pprint import pprint as ppimport 
from time import time
from operator import itemgetter
from sklearn.externals import joblib
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.ensemble import ExtraTreesClassifier as ETC
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import KFold
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

def sort_data(current_epoch,validation_set_prop = 0.20):
    '''this function conducts all of the additional steps required to
    pool the different data_frames in which the classifier features were compiled into
    a matrix.
    It was originally a large, unwieldy ipython notebook. Now it's just a large, 
    unwieldy function. 
    
    current_epoch is the two-week epoch to extract.
    validation_set_prop is the proportion of the data set to set aside as a
    "hold out" set.
    '''
    df = pd.read_pickle('df_steamdb_timeseries.pkl')
    drop_columns = ['fprice','iprice','price_date','sale_bool',
                'formatted_no_holiday','saledates_no_holiday',
               'sale_bool_all','min_iprice','mip_slopes','dirty_isi']
    df_feat_space = df.drop(drop_columns,axis=1)
    df_feat_space = df_feat_space[df_feat_space.formatted.map(type) != type([])]
    replacement_empty_list = list(df.iloc[1].sale_bool_no_holiday[0] - df.iloc[1].sale_bool_no_holiday[0][0] + (60*60*24*100.0))
    to_series = df_feat_space.since_sale_lists
    check = [x for x in to_series]
    check_copy = copy.deepcopy(check)
    
    just_one_epoch = list()
    for i,v in enumerate(check):
        if v == []:
            check_copy[i] = replacement_empty_list
        cur_epoch_time_since = check_copy[i][current_epoch]
        just_one_epoch.append(cur_epoch_time_since)
    
    df_feat_space['specific_epoch_time_since'] = just_one_epoch
    df_feat_space.has_price_slope = df_feat_space.has_price_slope.apply(lambda x:x*1)
    day_sec = 60 * 60 * 24
    twoweek_days = 14
    time_since_ds = (df_feat_space.specific_epoch_time_since / day_sec) + 14
    exp_lambda =  1/df_feat_space.dirty_isi_mean
    df_feat_space['exp_cdf_time_since_prob'] =  1 - np.exp(-time_since_ds * exp_lambda)
    df_steamscraped = pd.read_pickle('steam_features.pkl')
    df_steamscraped.head()
    drop_ss_cols = ['developer','game_name','meta_score','new_id','publisher','release_date','tag_data']
    df_ss_features = df_steamscraped.drop(drop_ss_cols,axis =1)
    df_ss_features.head()
    df_ss_features.big_publisher = df_ss_features.big_publisher.apply(lambda x:x*1) #turn into 1 or 0
    
    unique_pubs = df_ss_features.publisher_category.unique()
    le = LabelEncoder()
    le.fit(df_ss_features.publisher_category)
    df_ss_features['pub_cat_int'] = le.transform(df_ss_features.publisher_category)
    df_tag = pd.read_pickle('df_kmeans.pkl')
    df_tag_ss = pd.merge(left=df_ss_features,right=df_tag, left_on='appid', right_on='appid')
    df_merged_features = pd.merge(left=df_tag_ss,right=df_feat_space, left_on='appid', right_on='appid')
    df_merged_features['sale_count_x_dirty_isi_mean'] = df_merged_features.sale_count * df_merged_features.dirty_isi_mean
    df_merged_features['exp_specific_epoch_time_since'] = np.exp(-df_merged_features.specific_epoch_time_since)
    df_merged_features['sale_count_x_specific_epoch_time_since'] =df_merged_features.sale_count * df_merged_features.specific_epoch_time_since
    def get_initial_price(formatted_prices_dict):
        out_med = np.median(np.array([float(v['initial'].strip('$')) 
                  for v in formatted_prices_dict.itervalues()]))
        return out_med
    df_merged_features['median_initial_price'] = df_merged_features.formatted.apply(get_initial_price)
    
    yall = list()
    for i,v in enumerate(df_merged_features.sale_bool_no_holiday):
        if v == []:
            y_in = 0
        else:
            y_in = v[1][current_epoch] #1 is the index of the boolean list
        yall.append(y_in)
    
    yall = np.array(yall)
    analyzed_appids = df_merged_features.appid
    drop_more_columns = ['appid','formatted','since_sale_lists', 'sale_bool_no_holiday','publisher_category']
    df_merged_features = df_merged_features.drop(drop_more_columns,axis=1)
    Xall = df_merged_features.as_matrix().astype(np.float)
    
    total_rows = yall.size
    validation_size =  int(total_rows * 1.0 *  validation_set_prop)
    validation_row_indices = np.sort(np.random.choice(range(total_rows),validation_size, replace = False))
    traintest_row_indices =np.array(list(set(range(total_rows)) - set(list(validation_row_indices))))
    
    Xv = Xall[validation_row_indices,:]
    X = Xall[traintest_row_indices,:]
    Yv = yall[validation_row_indices]
    y = yall[traintest_row_indices]
    
    data = {'Xall': Xall, 'yall': yall, 'y':y, 'X':X, 'Yv': Yv, 'Xv':Xv, }
    return data

