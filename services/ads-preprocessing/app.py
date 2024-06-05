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





def load_write_AD(dataset_id=None, lon_bounds=None, lat_bounds=None, output_fs=None, ads_filename_nc=None):
    area = [
        lat_bounds[1],  # north
        lon_bounds[0],  # west
        lat_bounds[0],  # south
        lon_bounds[1],  # east
    ]
    
    c = cdsapi.Client()
    
    
    
    # Make sure to accept the terms and conditions on the CDS website before retrieval
    c.retrieve(
        dataset_id,
        {
            'variable': [
                'dust_aerosol_0.03-0.55um_mixing_ratio', 'dust_aerosol_0.55-0.9um_mixing_ratio', 'dust_aerosol_0.9-20um_mixing_ratio',
                'dust_aerosol_optical_depth_550nm', 'particulate_matter_10um', 'particulate_matter_1um',
                'particulate_matter_2.5um', 'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm',
                'total_aerosol_optical_depth_550nm', 'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm',
            ],
            'pressure_level': '1',
            'model_level': '1',
            'date': '2023-10-01/2023-12-01',
            'time': [
                '00:00', '03:00', '06:00',
                '09:00', '12:00', '15:00',
                '18:00', '21:00',
            ],
            'area': area,
            'format': 'netcdf',
        },
        ads_filename_nc
    )
    # chldataset = chldataset.sel(
    #     longitude=slice(*lon_bounds), latitude=slice(*lat_bounds)
    # )

    chldataset = chldataset[["CHL"]]

    if output_fs is None:
        chldataset.to_zarr(f"{dataset_id}.zarr/", mode="w")
    else:
        chldataset.to_zarr(
            output_fs.get_mapper(f"{GCS_BUCKET}/{dataset_id}.zarr/"),
            consolidated=True,
            mode="w",
        )










if __name__ == "__main__":

    CMEMS_USER = os.environ["CMEMS_USER"]
    CMEMS_PASS = os.environ["CMEMS_PASS"]

    fs = get_remote_filesystem()
    
    ads_filename_nc = "dust_ads.nc"

    load_write_CHL(
        dataset_id=DATASET_ID,
        lon_bounds=LON_BOUNDS,
        lat_bounds=LAT_BOUNDS,
        output_fs=fs
        ads_filename_nc = ads_filename_nc,
    )
