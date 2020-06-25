# import geoviews as gv
import param
import panel as pn
import pandas as pd
import holoviews as hv

from .covid_data import data

# gv.extension('bokeh')

VARS = ['Confirmed', 'Deaths', 'Recovered', 'Active', 'New']


class CovidMapper(param.Parameterized):
    date = param.Date(default=data['Date'].values[0])
    tiles = hv.element.tiles.CartoDark()

    @staticmethod
    def infection_map(date, variable):
        date = data['Date'].values[date]
        seldata = {
            'x': data['x'],
            'y': data['y'],
            'Confirmed': data.sel(Quantity='Confirmed', Date=date, Aggregation='Totals')['counts'],
            'Deaths': data.sel(Quantity='Deaths', Date=date, Aggregation='Totals')['counts'],
            'Recovered': data.sel(Quantity='Recovered', Date=date, Aggregation='Totals')['counts'],
            'Active': data.sel(Quantity='Active', Date=date, Aggregation='Totals')['counts'],
            'New': data.sel(Quantity='Confirmed', Date=date, Aggregation='Daily')['counts'],
            'Country': data['Country'],
        }
        points = hv.Points(seldata, kdims=['x', 'y'], vdims=VARS+['Country'])
        return CovidMapper.tiles * points.opts(
            size=hv.dim(variable).log()*5,
            logz=False,
            colorbar=True,
            fill_color=variable,
            fill_alpha=.5,
            line_color='gray', 
            cmap='viridis',
            width=1500, 
            responsive=True,
            # global_extent=True,
            tools=['hover'],
            active_tools=['pan', 'wheel_zoom'],
            show_legend=False,
        )
    
    def update_date(self, e):
        self.date = data['Date'].values[e.obj.value]
    
    @param.depends('date')
    def date_label(self):
        return f'## {pd.to_datetime(self.date).strftime("%m/%d/%Y")}'
    
    def panel(self):
        map_panel = pn.panel(
            hv.DynamicMap(
                self.infection_map, kdims=['day', 'variable']
            ).redim.range(day=(0, data['Date'].shape[0]-1)).redim.values(variable=VARS)
        )
        
        slider = map_panel[1][0][0]
        slider.param.watch(self.update_date, 'value')
        slider.width = 1400
        selector = map_panel[1][0][1]
        
        return pn.Column(map_panel[0], pn.Row(self.date_label, slider), selector)
