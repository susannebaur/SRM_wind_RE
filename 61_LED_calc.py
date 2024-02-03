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
LED_path = f'{wind_path}{RE_type}/LED/'

scens = set_ID.scens
area_setting = '_cw'

x_209 = sys.argv[2]

print(x_209)

qt_value=0.2

data = dict()
base = dict()
data_prepped = dict()

###### load data
for scen in scens:
    base[f'{scen}'] = xr.open_dataset(f'{LED_path}{scen}/LED_{RE_type}_base{area_setting}.nc',
                                            engine="netcdf4")

    data[f'{scen}'] = xr.open_dataset(f'{data_path}{scen}/{scen}_{RE_type}_209{x_209}_weekly_suit_prot_pop_{area_setting}.nc',
                                            engine="netcdf4")

    
    
    ########## get count of days
    # Calculate how many days per season are below the 20th percentile in this specific year
    low_energy_count_sea = dict()
    for sea in set_ID.seasons:
        # get 2015-24 value per season
        q_val_pres = base[scen]['tech_pot'].sel(season=sea)
        # get the seasonal data of the year
        data_sea = data[f'{scen}'].sel(time=data[f'{scen}']['time.season']==sea)['tech_pot']

        # count days where seasonal data is below the 20th percentile of seasonal 201 average
        low_energy_count_sea[sea] = data_sea.where(data_sea<q_val_pres).count(dim='time')
    # add days of all 4 seasons together
    low_energy_count_year = (low_energy_count_sea['DJF'].sum('member') + low_energy_count_sea['MAM'].sum('member') + low_energy_count_sea['JJA'].sum('member') + low_energy_count_sea['SON'].sum('member'))/6


    #save
    save_name=f'LED_{RE_type}_209{x_209}{area_setting}.nc'
    save_dir = f'/data/scratch/globc/baur/RE_analysis/wind/{RE_type}/LED/{scen}/'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass   

    low_energy_count_year.to_netcdf(save_dir + save_name)
    print(save_dir + save_name)



print('--------------------61_LED_calc.py ran successfully--------------------')