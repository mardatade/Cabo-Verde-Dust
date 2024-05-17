import copernicusmarine
import os


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

    chldataset.to_zarr(output_name, consolidated=True, mode="w")


def get_output_name(dataset_id=None):
    return dataset_id + ".zarr"


if __name__ == "__main__":

    dataset_id = "cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D"
    lon_bounds = (-28, -12)
    lat_bounds = (8, 22)

    CMEMS_USER = os.environ["CMEMS_USER"]
    CMEMS_PASS = os.environ["CMEMS_PASS"]

    load_write_CHL(
        dataset_id=dataset_id,
        lon_bounds=lon_bounds,
        lat_bounds=lat_bounds,
        output_name=get_output_name(dataset_id),
    )
