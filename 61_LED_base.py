import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib
import sys

import set_ID

import warnings
warnings.filterwarnings('ignore')

wind_path = set_ID.wind_path
RE_type = sys.argv[1]

plots_path = f'{wind_path}{RE_type}/plots/LED/'
data_path = f'{wind_path}{RE_type}/tech_pot_suit_prot_pop/'

scens = set_ID.scens
area_setting = '_cw'

qt_value=0.2

data = dict()
base = dict()
data_prepped = dict()

###### load data
for scen in scens:
    print(scen)
    # if base exists already just skip 
    file_name=f'LED_{RE_type}_base{area_setting}.nc'
    file_dir = f'/data/scratch/globc/baur/RE_analysis/wind/{RE_type}/LED/{scen}/'
    
    if not os.path.isfile(file_dir+file_name):

        for x in list(range(5,9+1)):
            print(x)
            base[f'{scen}_201{x}'] = xr.open_dataset(f'{data_path}{scen}/{scen}_{RE_type}_201{x}_weekly_suit_prot_pop_{area_setting}.nc',
                                                engine="netcdf4")
            
        
            ########## get quantiles
            # get the 20th percentile for each season
            data_interim = base[f'{scen}_201{x}'].groupby('time.season')#.quantile(qt_value, dim=qt_dim)
            ######### because of chunking error cannot do the quantile calc and have to do these lines below ################
            l = list()
            for name, group in data_interim:
                group=group.chunk(dict(time=-1))
                group = group.quantile(qt_value, dim='time')
                group.coords['season'] = name
                l.append(group)
            data_prepped[f'{scen}_201{x}'] = xr.concat(l, dim='season')

        data_prepped[f'{scen}_201']= xr.concat([data_prepped[f'{scen}_2015'], 
                                       data_prepped[f'{scen}_2016'], 
                                       data_prepped[f'{scen}_2017'], 
                                       data_prepped[f'{scen}_2018'], 
                                       data_prepped[f'{scen}_2019']
                                      ], dim='years').mean('years').mean('member')



        #save
        save_name=f'LED_{RE_type}_base{area_setting}.nc'
        save_dir = f'/data/scratch/globc/baur/RE_analysis/wind/{RE_type}/LED/{scen}/'
        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
        try:
            os.remove(save_dir + save_name)
        except:
            pass   

        data_prepped[scen+'_201'].to_netcdf(save_dir + save_name)
        print(save_dir + save_name)
        
    else:
        print(f'{file_dir}{file_name} exists already!')


print('--------------------61_LED_base.py ran successfully--------------------')
