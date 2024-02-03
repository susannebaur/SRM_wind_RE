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


## RE type
RE_type = set_ID.RE_type
## Scenario
scens = set_ID.scens
year = set_ID.year
year_ind = set_ID.year_ind
# aggregation
agg = set_ID.agg 
ID=set_ID.ID 
sensitivity_setting = set_ID.sensitivity_setting
area_setting = set_ID.area_setting
seasons=set_ID.seasons

if ID != '':
    data_path =  f'{set_ID.wind_path}{RE_type}/tech_pot_{ID}/'
elif ID == '':
    data_path = f'{set_ID.wind_path}{RE_type}/tech_pot/'
    
    
output_path = data_path

data = dict()
for scen in scens:   
    data[scen] = xr.open_dataset(f'{data_path}{scen}/{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}.nc',
                                        engine="netcdf4")

    try:
        data[f'{scen}'] = data[f'{scen}'].mean('height_over_orog_axis')
    except:
        pass


# calculate relative difference
diff = dict()

diff[f'ssp245_SAI'] = ((data[f'G6sulfur']['tech_pot'] - data[f'ssp245']['tech_pot']) / data[f'ssp245']['tech_pot']) * 100
diff[f'ssp585_SAI'] = ((data[f'G6sulfur']['tech_pot'] - data[f'ssp585']['tech_pot']) / data[f'ssp585']['tech_pot']) * 100
diff[f'ssp245_ssp585'] = ((data[f'ssp585']['tech_pot'] - data[f'ssp245']['tech_pot']) / data[f'ssp245']['tech_pot']) * 100

diff_scens = ['ssp245_SAI', 'ssp585_SAI', 'ssp245_ssp585']

#save relative difference
save_dir=output_path+'diff/'
for s in diff_scens:
    save_name=f'{s}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}_rel_diff.nc'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    try:
        os.remove(save_dir + save_name)
    except:
        pass
    diff[s].to_netcdf(save_dir+save_name)
    print(save_dir+save_name)


# get areas with statistically significant differences
pvals = dict()
diff_sig=dict()
diff_sig_out=dict()


if agg == 'seasonal_mean':
    for sea in seasons:
        SAI = data[f'G6sulfur']['tech_pot'].sel(season=sea)
        ssp2 = data[f'ssp245']['tech_pot'].sel(season=sea)
        ssp5 = data[f'ssp585']['tech_pot'].sel(season=sea)

        ttest_ssp2, pval_ssp2 = stats.ttest_rel(ssp2, SAI)
        ttest_ssp5, pval_ssp5 = stats.ttest_rel(ssp5, SAI)
        ttest_scens, pval_scens = stats.ttest_rel(ssp2, ssp5)

        pvals[f'ssp245_SAI'] = xr.DataArray(pval_ssp2, coords=SAI.mean('member').coords)
        pvals[f'ssp585_SAI'] = xr.DataArray(pval_ssp5, coords=SAI.mean('member').coords)
        pvals[f'ssp245_ssp585'] = xr.DataArray(pval_scens, coords=SAI.mean('member').coords)

        for s in diff_scens:
            diff_sig[f'{s}_{sea}'] = diff[s].sel(season=sea).mean('member').where(pvals[s]<0.05)

    # put the seasons back into one dataset
    for s in diff_scens:
        diff_sig_out[s] = xr.concat([diff_sig[f'{s}_DJF'], diff_sig[f'{s}_MAM'], diff_sig[f'{s}_JJA'], diff_sig[f'{s}_SON']], dim='season')
            
        diff_sig_out[s] = diff_sig_out[s].to_dataset(name='tech_pot')
                                   
        save_name=f'{s}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}_stat_sig.nc'
        save_dir=output_path+'diff/'

        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
        try:
            os.remove(save_dir + save_name)
        except:
            pass
        diff_sig_out[s].to_netcdf(save_dir+save_name)
        print(save_dir+save_name)
        
        
elif agg == 'all_mean':
    SAI = data[f'G6sulfur']['tech_pot']
    ssp2 = data[f'ssp245']['tech_pot']
    ssp5 = data[f'ssp585']['tech_pot']

    ttest_ssp2, pval_ssp2 = stats.ttest_rel(ssp2, SAI)
    ttest_ssp5, pval_ssp5 = stats.ttest_rel(ssp5, SAI)
    ttest_scens, pval_scens = stats.ttest_rel(ssp2, ssp5)

    pvals[f'ssp245_SAI'] = xr.DataArray(pval_ssp2, coords=SAI.mean('member').coords)
    pvals[f'ssp585_SAI'] = xr.DataArray(pval_ssp5, coords=SAI.mean('member').coords)
    pvals[f'ssp245_ssp585'] = xr.DataArray(pval_scens, coords=SAI.mean('member').coords)

    for s in diff_scens:
        diff_sig_out[f'{s}'] = diff[s].mean('member').where(pvals[s]<0.05).to_dataset(name='tech_pot')

        save_name=f'{s}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}_stat_sig.nc'
        save_dir=output_path+'diff/'

        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
        try:
            os.remove(save_dir + save_name)
        except:
            pass
        diff_sig_out[s].to_netcdf(save_dir+save_name)
        print(save_dir+save_name)
    
print('--------------------61_statistical_significance.py ran successfully--------------------')


    
    
    