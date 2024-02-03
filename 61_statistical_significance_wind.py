### set altitude! 'upper' or 'surface'
### set time_Setting '_seasonal' or ''
############################################

import set_ID
from pathlib import Path

import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools
import matplotlib.pyplot as plt

from scipy import stats
import pathlib

import warnings
warnings.filterwarnings('ignore')


import set_ID


## Scenario
scens = set_ID.scens
year = set_ID.year
year_ind = set_ID.year_ind
seasons=set_ID.seasons
members = set_ID.members
upper = slice(40000,20000)
lower = slice(85000,70000)
surface = slice(None,85000)

var = 'ua'
altitude = 'upper'
pressure_level=surface
t_sel='90' # '90' / '15'

time_setting = '_seasonal'


data=dict()

def load_data(t):
    T_data = dict()
    for scen in scens:
        single_members = dict()
        for i in members:
            single_mem = xr.open_mfdataset(f'/archive/globc/baur/CNRM_runs/RE_analysis/manual/{scen}_REdiff/AOESM_{scen}_REdiff_r{i}/merged/{var}_Amon_CNRM-ESM2-1_{scen}RE_r{i}i1p1f2_gr_20{t}01-*.nc', 
                                                engine="netcdf4")
            if time_setting == '_seasonal':
                single_members[str(i)] = single_mem.groupby('time.season').mean('time')
            else:
                single_members[str(i)] = single_mem.mean('time')

        T_data[scen] = xr.concat([single_members['1'],single_members['2'],single_members['3'],
                                     single_members['4'],single_members['5'],single_members['6']], dim='member')
        
    return T_data

for t in [t_sel]:
    data[t] = load_data(t)


data_sel=dict()

for scen in scens:
    data_sel[scen] = data[t_sel][scen].sel(plev=pressure_level).mean('plev')
    
# calculate relative and absolute difference
diff_rel = dict()
diff_abs = dict()

diff_rel[f'ssp245_SAI'] = ((data_sel[f'G6sulfur'][var] - data_sel[f'ssp245'][var]) / data_sel[f'ssp245'][var]) * 100
diff_rel[f'ssp585_SAI'] = ((data_sel[f'G6sulfur'][var] - data_sel[f'ssp585'][var]) / data_sel[f'ssp585'][var]) * 100
diff_rel[f'ssp585_ssp245'] = ((data_sel[f'ssp585'][var] - data_sel[f'ssp245'][var]) / data_sel[f'ssp245'][var]) * 100

diff_abs[f'ssp245_SAI'] = (data_sel[f'G6sulfur'][var] - data_sel[f'ssp245'][var]) 
diff_abs[f'ssp585_SAI'] = (data_sel[f'G6sulfur'][var] - data_sel[f'ssp585'][var]) 
diff_abs[f'ssp585_ssp245'] = (data_sel[f'ssp585'][var] - data_sel[f'ssp245'][var])

diff_scens = ['ssp245_SAI', 'ssp585_SAI', 'ssp585_ssp245']

#save relative difference
save_dir=f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/statistic_significant_diffs/'
for s in diff_scens:
    save_name_rel=f'{var}_{altitude}_{s}_{t_sel}_rel_diff{time_setting}.nc'
    save_name_abs=f'{var}_{altitude}_{s}_{t_sel}_abs_diff{time_setting}.nc'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    try:
        os.remove(save_dir + save_name_rel)
    except:
        pass
    try:
        os.remove(save_dir + save_name_abs)
    except:
        pass
    diff_rel[s].to_netcdf(save_dir+save_name_rel)
    diff_abs[s].to_netcdf(save_dir+save_name_abs)
    print(save_dir+save_name_rel)
    print(save_dir+save_name_abs)

# get areas with statistically significant differences
pvals = dict()
diff_sig_out=dict()

SAI = data_sel[f'G6sulfur'][var]
ssp2 = data_sel[f'ssp245'][var]
ssp5 = data_sel[f'ssp585'][var]

ttest_ssp2, pval_ssp2 = stats.ttest_rel(ssp2, SAI)
ttest_ssp5, pval_ssp5 = stats.ttest_rel(ssp5, SAI)
ttest_scens, pval_scens = stats.ttest_rel(ssp2, ssp5)

pvals[f'ssp245_SAI'] = xr.DataArray(pval_ssp2, coords=SAI.mean('member').coords)
pvals[f'ssp585_SAI'] = xr.DataArray(pval_ssp5, coords=SAI.mean('member').coords)
pvals[f'ssp585_ssp245'] = xr.DataArray(pval_scens, coords=SAI.mean('member').coords)

for s in diff_scens:
    diff_sig = diff_abs[s].mean('member').where(pvals[s]<0.05)

    diff_sig_out[s] = diff_sig.to_dataset(name='ua')

    save_name=f'{var}_{altitude}_{s}_{t_sel}_stat_sig{time_setting}.nc'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    try:
        os.remove(save_dir + save_name)
    except:
        pass
    diff_sig_out[s].to_netcdf(save_dir+save_name)
    print(save_dir+save_name)
