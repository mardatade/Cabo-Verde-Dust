import pandas as pd
import panel as pn
import xarray as xr
import hvplot.pandas
import hvplot.xarray

DUST_CSV = "https://storage.googleapis.com/2024-mardata-oscm-dust/dust.csv"
CHLA_DATA = "https://storage.googleapis.com/2024-mardata-oscm-dust/cmems_obs-oc_glo_bgc-plankton_nrt_l4-gapfree-multi-4km_P1D.zarr"


def load_dust_timeseries(location=DUST_CSV):
    """Load dust csv from given location."""
    return pd.read_csv(
        location,
        index_col=0,
        parse_dates=[
            0,
        ],
    )


def visualize_dust(df_dust, standardize=False):
    """Simplest possible plot."""
    if standardize:
        df_dust = df_dust / df_dust.max() * 100
    return df_dust.hvplot(grid=True)


def load_chla_fields(location=CHLA_DATA):
    """Load CHLa fields using zarr."""
    return xr.open_zarr(location)


def visualize_chla(ds_chla, time_step=0):
    return ds_chla.isel(time=time_step).hvplot()


standardize_selector = pn.widgets.Select(options=[True, False], name="Standardize?")

ds_chla = load_chla_fields(location=CHLA_DATA)
time_selector = pn.widgets.IntSlider(
    name="Selet Time", start=0, end=ds_chla.sizes["time"], step=1, value=0
)

template = pn.template.BootstrapTemplate(title="Cabo Verde Dust Visualisation")

template.sidebar.append(standardize_selector)
template.sidebar.append(time_selector)
template.main.append(
    pn.bind(
        visualize_dust, df_dust=load_dust_timeseries(), standardize=standardize_selector
    )
)
template.main.append(pn.bind(visualize_chla, ds_chla=ds_chla, time_step=time_selector))

template.servable()
