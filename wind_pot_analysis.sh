#!/bin/bash


#. ./set_ID.py
RE_type_info="offshore"
declare -a scens=("G6sulfur" "ssp245" "ssp585")
year="209"
power_curve_setting=""

################################################################################################################################
################################################################################################################################

# load python environments
source /data/scratch/globc/baur/Susanne_env39/bin/activate
module load python/gloesmfpy

#####run python scripts
###### loop over scenarios
for scen in ${scens[@]}
do
     ###### TECHNICAL POTENTIAL
     python 20_wind_tech_pot.py $scen
     
     if [ $power_curve_setting = "_nocutout" ];
     then
             python summation_nocutout.py $scen
     fi

     ###### REMAPPING TO IMAGE GRID
    python 30_remapping.py $scen   # this is for remapping of the tech_pot data
    python 32_remapping_wind.py $scen   # this is for "raw" wind data remapping   

    #### ICE-MASK
    if [ $RE_type_info = "offshore" ]; 
    then
            if [ ! -f "/data/scratch/globc/baur/RE_analysis/wind_masks/ice_mask/$scen/ice_mask_$year.nc" ]
            then
                    python 41_wind_ice_mask.py $scen
             else
                     echo "exists already: /data/scratch/globc/baur/RE_analysis/wind_masks/ice_mask/$scen/ice_mask_$year.nc"
             fi
     else
             echo "you chose onshore"              
     fi

      echo $scen "done"
done

python 40_LUC_suitability_wind.py     # doesn't depend on the CNRM scnearios and doesn't need to be rerun everytime.

python 50_multiplication_wind.py

python 61_statistical_significance_wind.py
python 61_statistical_significance_techpot.py

#if [ $agg = 'seasonal_mean' ];
#then	
#	python 61_statistical_significance_wind.py
#else
#	echo "no pvalue calculated"
#fi


######### deactivate current environment and activate baur-et-al-solar-RE because the regionmask package doesn't work in Susanne_env39 anymore 
deactivate
source /data/scratch/globc/baur/baur-et-al-solar-RE/bin/activate
#python 60_region_aggregation.py

echo "ALL DONE"
