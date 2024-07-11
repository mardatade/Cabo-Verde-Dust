#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 11:57:56 2024

@author: nparameswaran
"""

import cdsapi
import gcsfs
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from pathlib import Path
import os
import xarray as xr
from datetime import date, timedelta



GCS_BUCKET = "2024-mardata-oscm-dust"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", None)
DATASET_ID = "cams-global-reanalysis-eac4"
LON_BOUNDS = (-28, -12)
LAT_BOUNDS = (8, 22)

def get_remote_filesystem():
    try:
        fs = gcsfs.GCSFileSystem(project=PROJECT_ID, token="cloud")
        _ = fs.ls(GCS_BUCKET)
        return fs
    except:
        pass



def load_write_ADS(dataset_id=None, lon_bounds=None, lat_bounds=None, output_fs=None, ads_filename_grib=None):
    area = [
        lat_bounds[1],  # north
        lon_bounds[0],  # west
        lat_bounds[0],  # south
        lon_bounds[1],  # east
    ]
    
    c = cdsapi.Client()
    
    # get data from 01.01.2021 to previous day
    today = date.today()
    prevday = str(today- timedelta(days=1))
    print(prevday)
    #prevday = "2024-06-19"
    #print(prevday)

    
    # Make sure to accept the terms and conditions on the CDS website before retrieval
    #'particulate matter_10um', 'particulate_matter_1um',
    cdsapi.Client()

    variables = ['dust_aerosol_optical_depth_550nm', 
        'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm', 'total_aerosol_optical_depth_550nm',
        'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm']
    """
    c.retrieve(
    'cams-global-atmospheric-composition-forecasts',
    {
        'date': '2021-01-01/'+prevday,
        'type': 'forecast',
        'format': 'grib',
        'variable': [
                'dust_aerosol_optical_depth_550nm', 
        'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm', 'total_aerosol_optical_depth_550nm',
        'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm'
        ],
        'time': [
            '00:00', '12:00',
        ],
        'leadtime_hour': '0',
        'area': [
            22, -28, 8,
            -12,
        ],
    },
    'download_test_big.grib')
    """
    c.retrieve(
    'cams-global-atmospheric-composition-forecasts',
    {
        'date': '2021-01-01/'+prevday,
        'type': 'forecast',
        'format': 'grib',
        'variable': [
            'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm', 'total_aerosol_optical_depth_670nm',
        ],
        'time': [
            '00:00', '12:00',
        ],
        'leadtime_hour': '0',
        'area': [
            22, -28, 8,
            -12,
        ],
    },
    ads_filename_grib)


    return xr.load_dataset(ads_filename_grib, engine = "cfgrib", filter_by_keys={'typeOfLevel': 'hybrid'}) 


#########################
# Other possible parameters:

#, 'dust_aerosol_0.55-0.9um_mixing_ratio', 'dust_aerosol_0.9-20um_mixing_ratio',
#'dust_aerosol_optical_depth_550nm', 'particulate_matter_10um', 'particulate_matter_1um',
#'particulate_matter_2.5um', 'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm',
#'total_aerosol_optical_depth_550nm', 'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm',

# TO DO :
# How to individually download the paramteres(because of large size constraint) and stich the grib files together?

# https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-atmospheric-composition-forecasts?tab=form

###########################

if __name__ == "__main__":

    #CMEMS_USER = os.environ["CMEMS_USER"]
    #CMEMS_PASS = os.environ["CMEMS_PASS"]

    fs = get_remote_filesystem()
    
    ads_filename_grib = "dust_ads.grib"

    loaded_xr = load_write_ADS(
        dataset_id=DATASET_ID,
        lon_bounds=LON_BOUNDS,
        lat_bounds=LAT_BOUNDS,
        output_fs=fs,
        ads_filename_grib = ads_filename_grib,
    )





