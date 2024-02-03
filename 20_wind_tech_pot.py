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


LUC_path = set_ID.scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/regridded_and_selected/'
tech_pot_path = f'{set_ID.wind_path}/{set_ID.RE_type}/tech_pot/{sys.argv[1]}/'

raw_data_path = f'{set_ID.archive_path}{sys.argv[1]}_REdiff/'
prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/{sys.argv[1]}/'

members = set_ID.members
year = set_ID.year
height = set_ID.height
year = set_ID.year
power_curve_setting = set_ID.power_curve_setting

var_list = ['ua'+height,
            'va'+height,
            'siconca'
           ]

#### see if the windspeed file exists already. If yes, jump directly to tech pot calculation
try:
    ds_ = xr.open_mfdataset(f'{prepro_data_path}ws{height}_prepro_{year}.nc')
    print('windspeed file existed already')

except OSError:
    print('windspeed file needs to be built')
    ds_raw = dict()
    single_members = dict()


    for el in var_list:
        print(el)
        for i in members:
            single_members[str(i)] = xr.open_mfdataset(raw_data_path+'AOESM_'+sys.argv[1]+'_REdiff_r'+str(i)+'/merged/'+el+'_*_'+year+'*-*.nc',
                                            engine="netcdf4")

            single_members[str(i)] = single_members[str(i)].sel(time=slice(year+"0-01-01 01", str(int(year)+1)+"0-01-01 00"))

            try:
                single_members[str(i)] = single_members[str(i)].drop('time_bnds')
            except:
                single_members[str(i)] = single_members[str(i)].drop('time_bounds')
            try:
                single_members[str(i)] = single_members[str(i)].mean('height_over_orog_axis') 
            except:
                pass

        ds_raw[el] = xr.concat([single_members['1'],single_members['2'],single_members['3'],
                                single_members['4'],single_members['5'],single_members['6']], dim='member')
    print('data loaded')


    #ua wind is parallel to the x-axis. Positive u wind is from the west. Negative u wind is from the east. 
    #va wins runs parallel to the y-axis. Positive v wind is from the south. Negative v wind is from the north.

    ### Windspeed calculation
    ###### ws = sqrt(u^2+v^2) (square root of the sum of the squares)
    def ws_calc(ds_, h):
        return np.sqrt(ds_['ua'+h]['ua'+h]**2+ds_['va'+h]['va'+h]**2)
                           
    ds=ws_calc(ds_raw, height)
                           
    ##### save as file
    # turn to dataset
    ds_ = ds.to_dataset(name='ws')
    save_name = f'ws{height}_prepro_{year}.nc'
    save_dir = prepro_data_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
    ds_.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
                          
    # end of exception

                           
# save sea ice file
if set_ID.RE_type == 'offshore':
    ice_dict= dict()                       
    try:
        ice = xr.open_mfdataset(f'{prepro_data_path}siconca_prepro_{year}.nc')
    except OSError:
        single_members_ice = dict()
        
        for i in ['1','2']:
            single_members_ice[i] = xr.open_mfdataset(raw_data_path+'AOESM_'+sys.argv[1]+'_REdiff_r'+i+'/merged/siconca_*_'+year+'*-*.nc',
                                            engine="netcdf4", chunks={'time': 365})

            if year == '201':
                single_members_ice[str(i)] = single_members_ice[str(i)].sel(time=slice(year+"5-01-01 01", str(int(year)+1)+"5-01-01 00"))
            elif year == '202':
                single_members_ice[str(i)] = single_members_ice[str(i)].sel(time=slice(year+"5-01-01 01", str(int(year)+1)+"0-01-01 00"))
            else:
                single_members_ice[str(i)] = single_members_ice[str(i)].sel(time=slice(year+"0-01-01 01", str(int(year)+1)+"0-01-01 00"))
           

            try:
                single_members_ice[str(i)] = single_members_ice[str(i)].drop('time_bnds')
            except:
                single_members_ice[str(i)] = single_members_ice[str(i)].drop('time_bounds')
            try:
                single_members_ice[str(i)] = single_members_ice[str(i)].mean('height_over_orog_axis')
            except:
                pass

        ice = xr.concat([single_members_ice['1'],single_members_ice['2']], dim='member')

        # save file                       
        save_name = f'siconca_prepro_{year}.nc'
        save_dir = prepro_data_path
        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
        try:
            os.remove(save_dir + save_name)
        except:
            pass        
        ice.to_netcdf(save_dir + save_name)
        print(save_dir+save_name)

        # end of exception

    
### Technical potential

A = 1
a = 1 #km2
na = 0.97
nar = 0.9
if set_ID.RE_type == 'onshore':
    # power density
#    D = 6.4 # turbine spacing 6  -> 6.4 MW/km2 (use this for FLH calc)
    D = 1.56 # 1.56 turbines per km2   (use this for PWT calc)
      
    #PWT function parameters (from 1_windspeed_distribution script)
    a_ = 9.0112876712 
    b = 88.1921278770 
    c = 28.7390245618 
    d = 21.6199534039 
    # parameters for nocutout
    a_nco = 5.2762550001
    b_nco = 75499.3188179671
    c_nco = 787.4449790994

                
elif set_ID.RE_type == 'offshore':
 #   D = 5.3 # turbine spacing 12  -> 5.3 MW/km2
    D = 0.51 # 0.51 turbines per km2   (use this for PWT calc)
      
    #PWT function parameters (from 1_windspeed_distribution script)
    a_ = 24.5600807182
    b = 129.6477860229
    c = 24.9388367925
    d = 24.8750720898
    # parameters for nocutout
    a_nco = 12.9792322438
    b_nco= 153831.9959263891
    c_nco = 1181.9686894277
    
else:
    raise ValueError('Check RE_type setting')

def wind_tech_pot(scen, x):
    
    if power_curve_setting == '':
        PWT = a_*(1-np.exp(-x**2/b))*(1-np.exp(-x**2/c))*(np.exp(-x/d))
    
    elif power_curve_setting == '_nocutout':
        PWT = a_nco*(1-np.exp(-x**4/b_nco))*(1-np.exp(-x**2/c_nco))

    else:
        raise ValueError('Check power_curve_setting')
        
    tech_pot = (A * na * nar * a * D * PWT)
    
    try:
        tech_pot = tech_pot.rename({'ws':'tech_pot'})
    except KeyError:
        pass
    
        
    
    #save as file
    if power_curve_setting == '_nocutout':
        save_name = f'tech_pot_{scen}_{set_ID.RE_type}_{year}{power_curve_setting}_unsummed.nc'
    elif power_curve_setting == '':
        save_name = f'tech_pot_{scen}_{set_ID.RE_type}_{year}{power_curve_setting}.nc'
    else:
        raise ValueError('Problem setting save_name')
    save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
    tech_pot.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    
    return tech_pot


G6solar_wind_pot = wind_tech_pot(sys.argv[1], ds_) 
print('--------------------2_wind_tech_pot.py ran successfully--------------------')


