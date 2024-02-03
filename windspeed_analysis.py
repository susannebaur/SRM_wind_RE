import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib

import set_ID
import data_prep.data_prep as dataprep


archive_path = set_ID.archive_path
scens = set_ID.scens
members = set_ID.members

prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/'

wind=dict()

def load_data(t):
    for scen in scens:
        # import
        wind_data = xr.open_mfdataset(f'{prepro_data_path}{scen}/ws150m_prepro_{t}.nc')
        
        #area weighting
        weighted_ = dataprep.area_weighting_array(wind_data)
        #mean over members
        weighted_wind = weighted_.mean('time')
        
        #export
        weighted_wind.to_netcdf(f'{prepro_data_path}{scen}/ws150m_weighted_mean_{t}.nc')
        
    return wind_data

for t in ['201', '209']:
    wind[t] = load_data(t)



print('--------------------windspeed_analysis.py ran successfully-------------------')



