import copernicusmarine

dataset_id = "cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D"
output_name = dataset_id + ".nc"
lon_bounds = (-28, -12)
lat_bounds = (8, 22)

def load_write_CHL(dataset_id = None, lon_bounds = None, lat_bounds = None, output_name = None):
    chldataset = copernicusmarine.open_dataset(dataset_id=dataset_id)
    
    chldataset = chldataset.sel(
        longitude = slice(*lon_bounds),
        latitude = slice(*lat_bounds)
    )
    
    chldataset = chldataset[["CHL"]]
    
    chldataset.to_netcdf(output_name)


load_write_CHL(dataset_id, lon_bounds,  lat_bounds, output_name )
