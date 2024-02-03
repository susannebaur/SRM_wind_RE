import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

import pathlib
import importlib
import math


#own packages
import set_ID

xr.set_options(keep_attrs = True)

scen=sys.argv[1]

tech_pot_path = f'{set_ID.wind_path}/{set_ID.RE_type}/tech_pot/{scen}/'

members = set_ID.members
year = set_ID.year
height = set_ID.height
year = set_ID.year
power_curve_setting = set_ID.power_curve_setting


#load data
nocut = xr.open_mfdataset(f'{tech_pot_path}tech_pot_{scen}_{set_ID.RE_type}_{year}{power_curve_setting}_unsummed.nc')
norm = xr.open_mfdataset(f'{tech_pot_path}tech_pot_{scen}_{set_ID.RE_type}_{year}.nc')

#sum
summed = nocut + norm

#save file
save_name = f'tech_pot_{scen}_{set_ID.RE_type}_{year}_nocutout.nc'
save_dir = tech_pot_path
pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
try:
    os.remove(save_dir + save_name)
except:
    pass        
summed.to_netcdf(save_dir + save_name)




