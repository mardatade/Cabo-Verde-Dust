import pandas as pd
import panel as pn
import hvplot.pandas

DUST_CSV = "https://storage.googleapis.com/2024-mardata-oscm-dust/dust.csv"


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


standardize_selector = pn.widgets.Select(options=[True, False], name="Standardize?")

template = pn.template.BootstrapTemplate(title="Cabo Verde Dust Visualisation")

template.sidebar.append(standardize_selector)
template.main.append(
    pn.bind(
        visualize_dust, df_dust=load_dust_timeseries(), standardize=standardize_selector
    )
)

template.servable()
