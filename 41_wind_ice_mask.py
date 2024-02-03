import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

import pathlib
import importlib
from functools import reduce
import xesmf as xe

# import own packages
import set_ID

import warnings
warnings.filterwarnings("ignore")

year=set_ID.year

scratch_path = set_ID.scratch_path
ice_masks_path = set_ID.ice_masks_path


prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/{sys.argv[1]}/'


#load the datasets 
try:
    ice_CNRM = xr.open_dataset(prepro_data_path+f'siconca_prepro_{year}.nc',
                     engine='netcdf4')
    print('siconca file existed already in preprocessed')

except:
    single_members = dict()

    for i in ['1', '2']:
        single_members[str(i)] = xr.open_mfdataset(raw_data_path+'AOESM_'+sys.argv[1]+'_REdiff_r'+str(i)+'/merged/'+el+'_*_'+year+'0-'+year+'9.nc',
                                            engine="netcdf4")

        #single_members[str(i)] = single_members[str(i)].sel(time=slice(year+"0-01-01 01", str(int(year)+1)+"0-01-01 00"))
        try:
            single_members[str(i)] = single_members[str(i)].drop('time_bnds')
        except:
            single_members[str(i)] = single_members[str(i)].drop('time_bounds')

    ice_CNRM = xr.concat([single_members['1'],single_members['2']], dim='member')
    print('data loaded')



IMAGE = xr.open_dataset(f'{set_ID.RE_path}LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                    engine="netcdf4").rename({'latitude': 'lat', 'longitude':'lon'})



## Calculate seasonal max ice extent, remap to IMAGE grid, merge the masks and export
def ice_mask_calc(df):
    ice_mask=dict()
    seasons=['DJF', 'JJA', 'SON', 'MAM']
    for sea in seasons:

        ## Remap to IMAGE grid
        ds_in = df.groupby('time.season').max('time').sel(season=sea)['siconca']
        ds_out = xr.Dataset(
            {
                    "lat": (IMAGE["lat"]),
                    "lon": (IMAGE["lon"]),
            })

        regridder = xe.Regridder(ds_in, ds_out, "nearest_s2d", reuse_weights=True, periodic=True)
                              #   extrap_method="nearest_s2d") 
        regrid_ds = regridder(ds_in)
        mask_=regrid_ds.where(regrid_ds>5)
        ice_mask[sea] = mask_.fillna(1)
    # merge all seasons together
    sum_seasonal_masks = ice_mask['MAM']+ice_mask['DJF']+ice_mask['JJA']+ice_mask['SON']
    # create mask that takes only grid cells with >5% ice
    final_mask = sum_seasonal_masks.where(sum_seasonal_masks>5, other=1)  #### takes all cells with >5% ice
    # save mask
    save_dir = ice_masks_path+sys.argv[1]+'/'
    save_name = 'ice_mask_'+year+'.nc'
    final_mask.to_netcdf(save_dir+save_name)
    print(save_dir+save_name)
    return final_mask

ice_mask_calc(ice_CNRM)

print('--------------------4_ice_mask.py ran successfully--------------------')

