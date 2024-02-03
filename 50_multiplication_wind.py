import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib

#own packages
import set_ID
import data_prep.data_prep as dataprep



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
std=set_ID.std
thres=set_ID.thres
area_setting = set_ID.area_setting
power_curve_setting = set_ID.power_curve_setting

if ID != '':
    output_path =  f'{set_ID.wind_path}{RE_type}/tech_pot_{ID}/'
elif ID == '':
    output_path = f'{set_ID.wind_path}{RE_type}/tech_pot/'

############################## Include suitability factors in the tech pot calculation

_tech_pot_suit = dict()
IMAGE=dict()
tech_pot_path = set_ID.tech_pot_path
    
    
    
if RE_type == 'onshore':
    
    land_mask = xr.open_mfdataset(f'{set_ID.scratch_path}RE_analysis/LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                        engine="netcdf4").sel(time='2100-01-01').rename({'latitude':'lat', 'longitude':'lon'})
    
    ### Protected areas
    if 'prot' in ID:
        protected_areas = xr.open_mfdataset(f'{set_ID.protect_path}merged_protected_areas.nc',
                                            engine="netcdf4")
        protected_areas = protected_areas.fillna(-999)

        
        
    for scen in set_ID.scens:
        if agg == 'weekly':
            for x in list(range(5,9+1)):
                _tech_pot_suit[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}{x}_{agg}{power_curve_setting}.nc',
                                            engine="netcdf4")
                ### PV suitability factors
                if 'suit' in ID:
                    if 'LUC' in area_setting:

                         ### use ssp585 LUC as underlying for G6
                        if scen == 'G6sulfur' or scen == 'G6solar':
                            ssp='ssp5'
                        else:
                            #ssp='ssp5'
                            ssp=scen[:4]
                    else:
                        ssp='ssp2'
                    IMAGE[scen] = xr.open_dataset(f'{set_ID.LUC_path}{RE_type}_{ssp}_default.nc', 
                                         engine="netcdf4").rename({'latitude':'lat', 'longitude': 'lon'})


                ### population density distance weighting
                if 'pop' in ID:
                    if 'pop' in area_setting:
                        ### use ssp585 LUC as underlying for G6
                        if scen == 'G6sulfur' or scen == 'G6solar':
                            ssp='ssp5'.upper()
                        else:
                            #ssp='ssp5'
                            ssp=scen[:4].upper()
                    else:
                        ssp='SSP2'
                    pop_density = xr.open_mfdataset(f'{set_ID.pop_density_path}weighted_distance_std{str(std)}_thres{str(thres)}_209_{ssp}_exclhighpop.nc',
                                                    engine="netcdf4")


        # multiply to get the tech potential with the suitability factors

                #multiplication with suitability factors 
                if 'suit' in ID:
                    # choose middle of decade for IMAGE (2095, 2035,..)
                    if 'LUC' in area_setting:
                        _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = year+'5')['frac'].where(IMAGE[scen]['frac']>0).mean('time')       
                    else:
                        _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = '2095')['frac'].where(IMAGE[scen]['frac']>0).mean('time')  

                #pop density
                if 'pop' in ID:
                    _tech_pot_suit[scen] = _tech_pot_suit[scen] * pop_density['weighted_density']

                #remove protected areas
                if 'prot' in ID:
                    _tech_pot_suit[scen] = _tech_pot_suit[scen].where(protected_areas.mean('member')==-999)


                # remove values over the ocean
                _tech_pot_suit[scen] = _tech_pot_suit[scen].where(land_mask['GLCT']>0)   


                # set attributes
                _tech_pot_suit[scen].attrs['experiment_id'] = scen        

                #save as file
                save_name = f'{scen}_{RE_type}_{year}{x}_{agg}_{ID}_{sensitivity_setting}{area_setting}{power_curve_setting}.nc'
                save_dir = output_path+scen+'/'
                pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
                try:
                    os.remove(save_dir + save_name)
                except:
                    pass
                _tech_pot_suit[scen].to_netcdf(save_dir + save_name)
                print(save_dir + save_name)

        
        else: # if not weekly
            _tech_pot_suit[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}_{agg}{power_curve_setting}.nc',
                                        engine="netcdf4")
        
            ### PV suitability factors
            if 'suit' in ID:
                if 'LUC' in area_setting:

                     ### use ssp585 LUC as underlying for G6
                    if scen == 'G6sulfur' or scen == 'G6solar':
                        ssp='ssp5'
                    else:
                        #ssp='ssp5'
                        ssp=scen[:4]
                else:
                    ssp='ssp2'
                IMAGE[scen] = xr.open_dataset(f'{set_ID.LUC_path}{RE_type}_{ssp}_default.nc', 
                                     engine="netcdf4").rename({'latitude':'lat', 'longitude': 'lon'})


            ### population density distance weighting
            if 'pop' in ID:
                if 'pop' in area_setting:
                    ### use ssp585 LUC as underlying for G6
                    if scen == 'G6sulfur' or scen == 'G6solar':
                        ssp='ssp5'.upper()
                    else:
                        #ssp='ssp5'
                        ssp=scen[:4].upper()
                else:
                    ssp='SSP2'
                pop_density = xr.open_mfdataset(f'{set_ID.pop_density_path}weighted_distance_std{str(std)}_thres{str(thres)}_209_{ssp}_exclhighpop.nc',
                                                engine="netcdf4")


    # multiply to get the tech potential with the suitability factors

            #multiplication with suitability factors 
            if 'suit' in ID:
                # choose middle of decade for IMAGE (2095, 2035,..)
                if 'LUC' in area_setting:
                    _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = year+'5')['frac'].where(IMAGE[scen]['frac']>0).mean('time')       
                else:
                    _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = '2095')['frac'].where(IMAGE[scen]['frac']>0).mean('time')  

            #pop density
            if 'pop' in ID:
                _tech_pot_suit[scen] = _tech_pot_suit[scen] * pop_density['weighted_density']

            #remove protected areas
            if 'prot' in ID:
                _tech_pot_suit[scen] = _tech_pot_suit[scen].where(protected_areas.mean('member')==-999)


            # remove values over the ocean
            _tech_pot_suit[scen] = _tech_pot_suit[scen].where(land_mask['GLCT']>0)   


            # set attributes
            _tech_pot_suit[scen].attrs['experiment_id'] = scen        


            #save as file
            save_name = f'{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}{power_curve_setting}.nc'
            save_dir = output_path+scen+'/'
            pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
            try:
                os.remove(save_dir + save_name)
            except:
                pass
            _tech_pot_suit[scen].to_netcdf(save_dir + save_name)
            print(save_dir + save_name)
        
        
    ################## write global potential number out to .txt-file
    if ((agg == 'yearly_sum') and (power_curve_setting == '')):
        _tech_pot_suit_TWh = dict()

        ### output in PWh/yr
        outfile = open(f'{set_ID.wind_path}{RE_type}/global_tech_pop.txt', "a")
        print(ID)
        for scen in scens:
            print(scen)
            #do area weighting 
            _tech_pot_suit[scen] = dataprep.area_weighting_array(_tech_pot_suit[scen])
            #convert to TWh/yr 
            _tech_pot_suit_TWh[scen] =  _tech_pot_suit[scen].mean('time').mean('member') * 1e-6 
            #convert to PWh/yr
            print(str(round((_tech_pot_suit_TWh[scen]['tech_pot']/1000).sum().values.item(), 3)))
            outfile.write(ID+', '+scen+', '+str(year_ind)+', '+str(round((_tech_pot_suit_TWh[scen]['tech_pot']/1000).sum().values.item(), 3))+', '+sensitivity_setting+area_setting[1:]+"\n")
        outfile.close()

    print('--------------------5_multiplication.py ran successfully--------------------')

    
elif RE_type == 'offshore':
    print(year)
    for scen in scens:
        if agg == 'weekly':
            for x in list(range(5,9+1)):
                _tech_pot_suit[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}{x}_{agg}{power_curve_setting}.nc',
                                            engine="netcdf4")
        
                try:
                    _tech_pot_suit[scen] = _tech_pot_suit[scen].rename({'__xarray_dataarray_variable__':'tech_pot'})
                except ValueError:
                    pass
                _tech_pot_suit[scen] = _tech_pot_suit[scen]['tech_pot']

                # pop density weighting
                if 'pop' in ID:
                    if 'pop' in area_setting:
                        ### use ssp585 LUC as underlying for G6
                        if scen == 'G6sulfur' or scen == 'G6solar':
                            ssp='ssp5'.upper()
                        else:
                            #ssp='ssp5'
                            ssp=scen[:4].upper()
                    else:
                        ssp='SSP2'
                    pop_density = xr.open_mfdataset(f'{set_ID.pop_density_path}weighted_distance_std{str(std)}_thres{str(thres)}_209_{ssp}_exclhighpop.nc',
                                                    engine="netcdf4")

                    _tech_pot_suit[scen] = _tech_pot_suit[scen] * pop_density['weighted_density']


                if 'prot' in ID:
                    offshore_mask_prelim=xr.open_dataset(set_ID.offshore_mask_path+'offshore_wind_eez_protected_bathy.nc').mean('member')

                ## add the corresponding sea-ice-file
                if 'cw' in area_setting:
                    ssp='ssp245'
                    year_ice='209'
                else:
                    ssp=scen
                    year_ice = year
                sea_ice=xr.open_dataset(set_ID.ice_masks_path+ssp+'/ice_mask_'+year_ice+'.nc',
                                 engine='netcdf4').mean('member')

                # add sea_ice mask to the other masks
                offshore_mask = offshore_mask_prelim.where(sea_ice['siconca']==1)
                # remove Antarctic values
                offshore_mask['tech_pot'].loc[slice(-70, -89)] = None

                _tech_pot_suit[scen]=_tech_pot_suit[scen].where(offshore_mask['tech_pot']>0)
                _tech_pot_suit[scen] = _tech_pot_suit[scen].to_dataset(name='tech_pot')

                #save as file
                save_name = f'{scen}_{RE_type}_{year}{x}_{agg}_{ID}_{sensitivity_setting}{area_setting}{power_curve_setting}.nc'
                save_dir = output_path+scen+'/'
                pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
                try:
                    os.remove(save_dir + save_name)
                except:
                    pass
                _tech_pot_suit[scen].to_netcdf(save_dir + save_name)
                print(save_dir + save_name)
        
        
        
        else: # not weekly
        
            _tech_pot_suit[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}_{agg}{power_curve_setting}.nc',
                                            engine="netcdf4")
            try:
                _tech_pot_suit[scen] = _tech_pot_suit[scen].rename({'__xarray_dataarray_variable__':'tech_pot'})
            except ValueError:
                pass
            _tech_pot_suit[scen] = _tech_pot_suit[scen]['tech_pot']

            # pop density weighting
            if 'pop' in ID:
                if 'pop' in area_setting:
                    ### use ssp585 LUC as underlying for G6
                    if scen == 'G6sulfur' or scen == 'G6solar':
                        ssp='ssp5'.upper()
                    else:
                        #ssp='ssp5'
                        ssp=scen[:4].upper()
                else:
                    ssp='SSP2'
                pop_density = xr.open_mfdataset(f'{set_ID.pop_density_path}weighted_distance_std{str(std)}_thres{str(thres)}_209_{ssp}_exclhighpop.nc',
                                                engine="netcdf4")

                _tech_pot_suit[scen] = _tech_pot_suit[scen] * pop_density['weighted_density']


            if 'prot' in ID:
                offshore_mask_prelim=xr.open_dataset(set_ID.offshore_mask_path+'offshore_wind_eez_protected_bathy.nc').mean('member')

            ## add the corresponding sea-ice-file
            if 'cw' in area_setting:
                ssp='ssp245'
                year_ice='209'
            else:
                ssp=scen
                year_ice=year
            sea_ice=xr.open_dataset(set_ID.ice_masks_path+ssp+'/ice_mask_'+year_ice+'.nc',
                             engine='netcdf4').mean('member')

            # add sea_ice mask to the other masks
            offshore_mask = offshore_mask_prelim.where(sea_ice['siconca']==1)
            # remove Antarctic values
            offshore_mask['tech_pot'].loc[slice(-70, -89)] = None

            _tech_pot_suit[scen]=_tech_pot_suit[scen].where(offshore_mask['tech_pot']>0)
            _tech_pot_suit[scen] = _tech_pot_suit[scen].to_dataset(name='tech_pot')

            #save as file
            save_name = f'{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}{power_curve_setting}.nc'
            save_dir = output_path+scen+'/'
            pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
            try:
                os.remove(save_dir + save_name)
            except:
                pass
            #save file
            _tech_pot_suit[scen].to_netcdf(save_dir + save_name)
            print(save_dir + save_name)
        
        
    ################## write global potential number out to .txt-file
    if ((agg == 'yearly_sum') and (power_curve_setting == '')):
        _tech_pot_suit_TWh = dict()

        ### output in PWh/yr
        outfile = open(f'{set_ID.wind_path}{RE_type}/global_tech_pop.txt', "a")
        print(ID)
        for scen in scens:
            print(scen)
            #do area weighting 
            _tech_pot_suit[scen] = dataprep.area_weighting_array(_tech_pot_suit[scen])
            #convert to TWh/yr 
            _tech_pot_suit_TWh[scen] =  _tech_pot_suit[scen].mean('time').mean('member') * 1e-6 
            #convert to PWh/yr
            print(str(round((_tech_pot_suit_TWh[scen]['tech_pot']/1000).sum().values.item(), 3)))
            outfile.write(ID+', '+scen+', '+str(year_ind)+', '+str(round((_tech_pot_suit_TWh[scen]['tech_pot']/1000).sum().values.item(), 3))+', '+sensitivity_setting+', '+area_setting[1:]+"\n")
        outfile.close()

    print('--------------------5_multiplication.py ran successfully--------------------')
    
else:
    raise AssertionError('RE_type in 5_multiplication.py script missing')
    