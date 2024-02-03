# Script to create mask for suitable regions -> exports .nc file 2015-2100 with suitability factors

#agricultural land (1), 
#extensive grassland (2), 
#carbon plantation (3), 
#regrowth forest abandoning (4),
#regrowth forest timber (5), 
#biofuels(6), 
#ice (7), 
#tundra (8), 
#wooded tundra (9), 
#boreal forest (10), 
#cool conifer forest (11), 
#temp. mixed forest (12), 
#temp. decid. forest (13), 
#warm mixed forest (14), 
#grassland/steppe (15),
#hot desert (16), 
#scrubland (17), 
#savanna (18), 
#tropical woodland (19), 
#tropical forest (20)

###### wind: 1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,18

import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

from functools import reduce
import pathlib

import set_ID

dirloc_scylla = '/data/home/globc/baur/jupyter_notebook_scripts/RE_analysis/'
scratch_path = set_ID.scratch_path
ds_path = scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/regridded_and_selected/'


IMAGE_raw_SSP2 = xr.open_dataset(scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                    engine="netcdf4")
IMAGE_raw_SSP5 = xr.open_dataset(scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/SSP5/GLCT.nc',
                                    engine="netcdf4")

# take only years from 2015
IMAGE2 = IMAGE_raw_SSP2.sel(time = slice('2015', '2100'))
IMAGE5 = IMAGE_raw_SSP5.sel(time = slice('2015', '2100'))

#### Suitability fractions and ds export
#regions=[1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,18]
regions = [1,2,6,8,9,15,16,17,18]
LUC_fractions = dict()
LUC_fractions['default'] = [0.05, 0.15, 0.05, 0.2, 0.1, 0.2, 0.4, 0.2, 0.15]


    
def LUC_mask(IMAGE_ds, ssp, k):
    # use only datapoints that are suitable
    mask = reduce(lambda x,y: np.logical_or(x, IMAGE_ds['GLCT']==y), regions, False)
    suitable_LUC = IMAGE_ds.where(mask)
    
    #### assign a suitability fraction to a LUC
    LUC_masks = dict()
    for val, frac in zip(regions, LUC_fractions[k]):
        mask = suitable_LUC.where(suitable_LUC['GLCT']==val)  #dataset with only the one LUC
        frac = mask.where(mask['GLCT'] != val, frac).rename({'GLCT': 'frac'}) #new dataset replace LUC value with fraction
        LUC_masks['mask'+str(val)] = xr.merge([mask, frac]) # merge the GLCT and frac dataset to have two variables
    suitability_ds = xr.merge(list(LUC_masks.values()))
    
    ####save
    save_name = set_ID.RE_type+'_'+ssp+'_'+k+'.nc'
    save_dir = ds_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    suitability_ds.to_netcdf(save_dir + save_name)
    
    return suitability_ds
      
LUC_mask(IMAGE5, 'ssp5', 'default')
LUC_mask(IMAGE2, 'ssp2', 'default')



print(set_ID.RE_type+'-suitability files exported')

print('--------------------LUC_suitability.py ran successfully--------------------')
