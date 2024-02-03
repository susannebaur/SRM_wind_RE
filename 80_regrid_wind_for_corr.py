import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools
import xesmf as xe

import pathlib

import warnings
warnings.filterwarnings('ignore')

import set_ID
import data_prep.data_prep as dataprep
import importlib
importlib.reload(set_ID)

archive_path = set_ID.archive_path
wind_path = set_ID.wind_path
plots_path = f'{wind_path}/onoffshore/plots/'
data_path = f'{wind_path}'
prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/'

scens = set_ID.scens
members = set_ID.members
agg=set_ID.agg

wind=dict()

def load_data(t):
    wind_data = dict()
    for scen in scens:
        wind_data[scen] = xr.open_mfdataset(f'{prepro_data_path}{scen}/ws150m_prepro_{t}.nc').mean('time')
    return wind_data

for t in ['201', '209']:
    wind[t] = load_data(t)

# load grid data
# IMAGE data
IMAGE_raw = xr.open_dataset(set_ID.scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                    engine="netcdf4")
IMAGE = IMAGE_raw.rename({'latitude': 'lat', 'longitude':'lon'})

# target grid
ds_out = xr.Dataset(
    {
            "lat": (IMAGE["lat"]),
            "lon": (IMAGE["lon"]),
    })


#regrid
for scen in scens:
    for t in ['201', '209']:
        ds_in = wind[t][scen] #pot_nofrac
        regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True, periodic=True)
        regrid_ds = regridder(ds_in)
        regrid_ds.attrs = ds_in.attrs
        regrid_ds.to_netcdf(f'{prepro_data_path}{scen}/ws150m_10ymean_regridded_{t}.nc')
        print(f'{prepro_data_path}{scen}/ws150m_10ymean_regridded_{t}.nc')


print('--------------- 80_regrid_wind_for_corr.py ran successfully -------------------')
    

    
    
    
    
    