import pandas as pd
import xarray as xr
from pathlib import Path
import datetime
import numpy as np
from glob import glob
from pyproj import Transformer

VARS = ['Confirmed', 'Deaths', 'Recovered']

base_dir = Path(__file__).absolute().resolve().parent
data_dir = (base_dir / '../COVID-19/csse_covid_19_data').resolve()


def combine_key(row):
    key = row['Country/Region']
    state = row['Province/State']
    if state == state:
        key = f'{state},{key}'
    return key


def load_data():

    time_series_path = data_dir / 'csse_covid_19_time_series' / 'time_series_covid19_{VAR}_global.csv'

    # dfs = list()
    # dims = ['Aggregation', 'Quantity', 'Region', 'Date']
    # for var in VARS[:-1]:
    #     df = pd.read_csv(time_series_path.as_posix().format(VAR=var.lower()))
    #     df.insert(0, 'combined_key', df.apply(combine_key, axis=1))
    #     df.sort_values(by='combined_key', inplace=True)
    #     dfs.append(df)
    #
    # recovered_df = df = pd.read_csv(time_series_path.as_posix().format(VAR=VARS[-1].lower()))
    # recovered_df.loc[recovered_df['Country/Region'] == 'Canada', 'Province/State'] = 'Recovered'
    # recovered_df.insert(0, 'combined_key', df.apply(combine_key, axis=1))
    # confirmed_df = dfs[0]
    # recovered_df = recovered_df.merge(confirmed_df[['combined_key', 'Province/State', 'Country/Region', 'Lat', 'Long']],
    #                                   indicator=False, how='outer')
    # recovered_df.drop([157, 190, 226, 234], axis=0, inplace=True)
    # recovered_df.sort_values(by='combined_key', inplace=True)
    # dfs.append(recovered_df)
    #
    # data_vars = [df.iloc[:, 4:].values for df in dfs]
    # data_vars.append(data_vars[0] - data_vars[1] - data_vars[2])   # active cases
    # VARS.append('Active')
    # data_vars = np.stack(data_vars)
    # data_vars = np.stack((data_vars, np.diff(data_vars, axis=-1, n=1, prepend=0)))  # daily changes
    # data_vars = {'counts': (dims, np.stack(data_vars))}

    dfs = list()
    dims = ['Aggregation', 'Quantity', 'Country', 'Date']
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    for var in VARS:
        df = pd.read_csv(time_series_path.as_posix().format(VAR=var.lower()))
        df.rename({'Country/Region': 'Country'}, axis=1, inplace=True)
        lat_lon = df[['Country', 'Lat', 'Long']]
        lat_lon = lat_lon.groupby('Country').first()
        lat_lon['x_y'] = lat_lon.apply(lambda row: transformer.transform(row.Lat, row.Long), axis=1)
        lat_lon['x'] = lat_lon.x_y.apply(lambda z: z[0])
        lat_lon['y'] = lat_lon.x_y.apply(lambda z: z[1])
        df.drop(['Lat', 'Long'], axis=1, inplace=True)
        df = df.groupby('Country').sum()
        df.insert(0, 'y', lat_lon['y'])
        df.insert(1, 'x', lat_lon['x'])
        df.sort_values(by='Country', inplace=True)
        dfs.append(df)
    data_vars = [df.iloc[:, 2:].values for df in dfs]
    data_vars.append(data_vars[0] - data_vars[1] - data_vars[2])  # active cases
    VARS.append('Active')
    data_vars = np.stack(data_vars)
    data_vars = np.stack((data_vars, np.diff(data_vars, axis=-1, n=1, prepend=0)))  # daily changes
    data_vars = (data_vars + np.absolute(data_vars)) / 2
    data_vars = {'counts': (dims, data_vars)}

    coords = dict(
        Country=('Country', df.index),
        Date=df.columns.tolist()[2:],
        x=('Country', df['x']),
        y=('Country', df['y']),
        Quantity=VARS,
        Aggregation=['Totals', 'Daily']
    )
    return xr.Dataset(data_vars=data_vars, coords=coords)


def load_totals():
    daily_reports_path = data_dir / 'csse_covid_19_daily_reports' / '{DATE}.csv'

    today = datetime.datetime.now()
    yesterday = (today - datetime.timedelta(1))
    daily_files = sorted(glob('/Users/rditlsc9/Workspace/covid-19-dashboard/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv'))
    yesterday_file, today_file = daily_files[-2:]
    df_today = pd.read_csv(today_file)
    df_yesterday = pd.read_csv(yesterday_file)

    today_totals = df_today[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum()
    yesterday_totals = df_yesterday[['Confirmed', 'Deaths', 'Recovered', 'Active']].sum()

    return today_totals, yesterday_totals


data = load_data()
