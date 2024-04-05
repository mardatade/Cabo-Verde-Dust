import click

from pathlib import Path
import os

import pandas as pd
import numpy as np
import pooch
import xarray as xr

import gcsfs
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.dirfs import DirFileSystem

DATA_PATH = "2024-mardata-oscm-dust/"
LOCAL_PREFIX = "/data/"
DUST_CSV = "dust.csv"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", None)
MIN_DATE = "2021-01-01"


def get_local_or_remote_filesystem():
    """Get either remote or a local filesystem."""
    try:
        fs = gcsfs.GCSFileSystem(project=PROJECT_ID, token="cloud")
        _ = fs.ls(DATA_PATH)
        return fs
    except:
        local_prefix = Path(LOCAL_PREFIX)
        local_prefix.mkdir(exist_ok=True, parents=True)
        fs = DirFileSystem(
            path=local_prefix,
            fs=LocalFileSystem(auto_mkdir=True),
        )
        fs.makedirs(DATA_PATH, exist_ok=True)
        _ = fs.ls(DATA_PATH)
        return fs


def write_df_to_csv(df, filename=None, fs=None, **kwargs):
    """Write df to CSV either locally or remotely.

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe containing an index called "time" and a column called "dust".
    filename: str
        Name of the output file.
    fs: fsspec Filesystem
        Defaults to None in which case a filesystem is found automatically.

    **kwargs are passed to pandas.to_csv().
    """
    if fs is None:
        fs = get_local_or_remote_filesystem()
    with fs.open(str(Path(DATA_PATH) / filename), mode="wb") as f:
        df.to_csv(f, **kwargs)


def read_df_from_csv(filename=None, fs=None, **kwargs):
    """Write df to CSV either locally or remotely.

    Parameters
    ----------
    filename: str
        Name of the file.
    fs: fsspec Filesystem
        Defaults to None in which case a filesystem is found automatically.

    **kwargs are passed to pandas.read_csv().
    """
    try:
        if fs is None:
            fs = get_local_or_remote_filesystem()
        with fs.open(str(Path(DATA_PATH) / filename), mode="rb") as f:
            return pd.read_csv(f, **kwargs)
    except Exception as e:
        print(e)


def read_cloudnet_metadata_mindelo(min_date=None):
    """Read midelo lidar metadata from cloudnet.

    Parameters
    ----------
    min_date: str | datestamp
        Crop before this date.

    Returns
    -------
    pandas.DataFrame

    """
    df = pd.read_json("https://cloudnet.fmi.fi/api/files?site=mindelo&product=lidar")
    df["measurementDate"] = pd.to_datetime(df["measurementDate"])
    df = df.set_index("measurementDate")
    df = df.where(df.instrumentId == "pollyxt").dropna(how="all")

    df = df.sort_index()
    df = df.loc[min_date:]

    return df


def download_resample_remove(url=None, known_hash=None, resample_to=None):
    """Download netCDF file, open, rewsample, and remove file.

    Parameters
    ----------
    url: str
        URL of the netCDF file.
    known_hash: str
        Hash of the file.
    resample_to: str
        Frequency to which to resample the dataset

    Returns
    -------
    xr.Dataset

    """
    f = Path(pooch.retrieve(url, known_hash=known_hash))
    _ds = xr.open_dataset(f)
    ds = _ds[["depolarisation"]].resample(time=resample_to).mean().compute().copy()
    _ds.close()
    f.unlink()
    return ds


def download_and_concat(df_metadata=None, resample_to=None, nfiles=None):
    """Download all netCDF files, open, resample, cleanup, concat.

    Parameters
    ----------
    df_metadata: pd.DataFrame
        Contains a time-index and the columns "downloadUrl" and "checksum".
    resample_to: str
        Frequency to which to resample the dataset
    nfiles: int
        Number of most recent files to download. Defaults to None (i.e. all files).

    Returns
    -------
    xr.Dataset

    """
    if nfiles is None:
        nfiles = 0
    return xr.concat(
        [
            download_resample_remove(
                url=_url, known_hash=_hash, resample_to=resample_to
            )
            for _url, _hash in list(
                zip(
                    df_metadata.iloc[nfiles:]["downloadUrl"],
                    df_metadata.iloc[nfiles:]["checksum"],
                )
            )
        ],
        dim="time",
    )


def get_near_surface_dust(ds, resample_to=None, range_min=None, range_max=None):
    """Estimate near-surface dust.

    Parameters
    ----------
    ds: xarray.Dataset
        Contains a variable "depolarisation" and coordinate "range".
    resample_to: str
        Frequency to which to resample the dataset
    range_min: float
        Minimal range in meters above the instrument.
    range_max: float
        Maximum range in meters above the instrument.

    Returns
    -------
    pd.DataFrame

    """
    return (
        ds.resample(time=resample_to)
        .asfreq()
        .sel(range=slice(50, 200))
        .mean("range")
        .depolarisation.rename("dust")
        .to_dataframe()
    )


@click.command()
@click.option(
    "--frequency", default="6h", help="Frequency to resample to. Default is '6h'"
)
@click.option(
    "--range_min",
    default=50.0,
    help="Minimal range in meters above the instrument. Defaults to 50.0",
)
@click.option(
    "--range_max",
    default=200.0,
    help="Maximal range in meters above the instrument. Defaults to 200.0",
)
@click.option(
    "--num_files",
    default=None,
    type=int,
    help="Max number of files to be read.",
)
def main(frequency, range_min, range_max, num_files):
    print("Resampling to --", frequency)
    print("Range from", range_min, "to", range_max)

    try:
        df_dust_existing = read_df_from_csv(
            filename=DUST_CSV,
            index_col=0,
            parse_dates=[
                0,
            ],
        )
        all_days = sorted(df_dust_existing.index.to_series().dt.date.unique())
        last_day = all_days[-1]
        df_metadata = read_cloudnet_metadata_mindelo(min_date=last_day)
        df_dust_existing = df_dust_existing.loc[: all_days[-2]]
    except Exception as e:
        df_metadata = read_cloudnet_metadata_mindelo(min_date=MIN_DATE)
        df_dust_existing = None

    ds_lidar = download_and_concat(
        df_metadata=df_metadata, resample_to=frequency, nfiles=num_files
    )
    df_dust_new = get_near_surface_dust(
        ds=ds_lidar, resample_to=frequency, range_min=range_min, range_max=range_max
    )
    df_dust = pd.concat([df_dust_existing, df_dust_new])
    write_df_to_csv(df=df_dust, filename=DUST_CSV)
    df_dust_reread = read_df_from_csv(
        filename=DUST_CSV,
        index_col=0,
        parse_dates=[
            0,
        ],
    )

    print("orig df:", df_dust)
    print("reread df:", df_dust_reread)


if __name__ == "__main__":
    main()
