import copernicusmarine

import click
import os

dataset_id = "cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D"
output_name = dataset_id + ".nc"
lon_bounds = (-28, -12)
lat_bounds = (8, 22)


CMEMS_USER = os.environ["CMEMS_USER"]
CMEMS_PASS = os.environ["CMEMS_PASS"]


def load_write_CHL(dataset_id=None, lon_bounds=None, lat_bounds=None, output_name=None):
    chldataset = copernicusmarine.open_dataset(
        dataset_id=dataset_id,
        username=CMEMS_USER,
        password=CMEMS_PASS,
    )

    chldataset = chldataset.sel(
        longitude=slice(*lon_bounds), latitude=slice(*lat_bounds)
    )

    chldataset = chldataset[["CHL"]]

    chldataset.to_netcdf(output_name)


def get_output_name(dataset_id=None):
    return dataset_id + ".nc"


@click.command()
@click.option(
    "--dataset_id",
    default="cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D",
    help="Chla dataset id from cmems.",
)
@click.option(
    "--lon_start",
    default=-28.0,
    help="Lon start",
)
@click.option(
    "--lon_end",
    default=-12.0,
    help="Lon end",
)
@click.option(
    "--lat_start",
    default=8.0,
    help="Lat start",
)
@click.option(
    "--lat_end",
    default=22.0,
    help="Lat end",
)
def main(dataset_id, lon_start, lon_end, lat_start, lat_end):
    load_write_CHL(
        dataset_id,
        lon_bounds=(lon_start, lon_end),
        lat_bounds=(lat_start, lat_end),
        output_name=get_output_name(dataset_id),
    )


if __name__ == "__main__":
    main()
