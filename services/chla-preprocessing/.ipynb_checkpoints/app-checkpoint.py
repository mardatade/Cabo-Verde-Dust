import copernicusmarine
import os

import gcsfs
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.dirfs import DirFileSystem
from pathlib import Path


GCS_BUCKET = "2024-mardata-oscm-dust"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", None)
DATASET_ID = "cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D"
LON_BOUNDS = (-28, -12)
LAT_BOUNDS = (8, 22)


def get_remote_filesystem():
    """Get either remote or a local filesystem."""
    try:
        fs = gcsfs.GCSFileSystem(project=PROJECT_ID, token="cloud")
        _ = fs.ls(GCS_BUCKET)
        return fs
    except:
        pass


def load_write_CHL(dataset_id=None, lon_bounds=None, lat_bounds=None, output_fs=None):
    chldataset = copernicusmarine.open_dataset(
        dataset_id=dataset_id,
        username=CMEMS_USER,
        password=CMEMS_PASS,
    )

    chldataset = chldataset.sel(
        longitude=slice(*lon_bounds), latitude=slice(*lat_bounds)
    )

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

    load_write_CHL(
        dataset_id=DATASET_ID,
        lon_bounds=LON_BOUNDS,
        lat_bounds=LAT_BOUNDS,
        output_fs=fs,
    )
