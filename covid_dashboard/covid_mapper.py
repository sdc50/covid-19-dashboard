import geoviews as gv
import param
import panel as pn
import holoviews as hv

from .covid_data import data

# gv.extension('bokeh')

VARS = ['Confirmed', 'Deaths', 'Recovered', 'Active', 'New']


class CovidMapper(param.Parameterized):
    date = param.String(default=data['Date'].values[0])
    tiles = gv.tile_sources.CartoDark

    @staticmethod
    def infection_map(date, variable):
        date = data['Date'].values[date]
        seldata = {
            'longitude': data['longitude'], 
            'latitude': data['latitude'], 
            'Confirmed': data.sel(Quantity='Confirmed', Date=date, Aggregation='Totals')['counts'],
            'Deaths': data.sel(Quantity='Deaths', Date=date, Aggregation='Totals')['counts'],
            'Recovered': data.sel(Quantity='Recovered', Date=date, Aggregation='Totals')['counts'],
            'Active': data.sel(Quantity='Active', Date=date, Aggregation='Totals')['counts'],
            'New': data.sel(Quantity='Confirmed', Date=date, Aggregation='Daily')['counts'],
            'Country': data['Country'],
        }
        points = gv.Points(seldata, kdims=['longitude', 'latitude'], vdims=VARS+['Country'])
        return CovidMapper.tiles * points.opts(
            size=gv.dim(variable).log()*5,
            logz=True,
            fill_color=variable,
            fill_alpha=.5,
            line_color='gray', 
            cmap='fire_r',
            width=1500, 
            height=700,
            global_extent=True, 
            tools=['hover'],
            active_tools=['pan', 'wheel_zoom'],
            show_legend=False,
        )
    
    def update_date(self, e):
        self.date = data['Date'].values[e.obj.value]
    
    @param.depends('date')
    def date_label(self):
        return f'## {self.date}'
    
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
