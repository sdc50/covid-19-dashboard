import numpy as np
import param
import panel as pn
import holoviews as hv

from .covid_data import data

hv.extension('bokeh')


class CovidPlotter(param.Parameterized):
    plot_type = param.ObjectSelector(default='Curve', objects=['Bar', 'Curve'], precedence=0.1)
    aggregation = param.ObjectSelector(default='Totals', objects=data.coords['Aggregation'].values, precedence=0.2)
    quantity = param.ObjectSelector(default='All', objects=['All'] + list(data.coords['Quantity'].values), precedence=0.2)
    groupby = param.ObjectSelector(default='Global', precedence=0.4, objects=['Global', 'Country'], label='Group By')
    countries = param.ListSelector(default=['China', 'US', 'Italy', 'France'], objects=np.unique(data.coords['Country'].values))
    # states = param.ListSelector(default=['Utah', 'Mississippi', 'California'], objects=[])
    selected_data = param.ClassSelector(hv.Dataset, precedence=-1)

    def __init__(self, **params):
        super().__init__(**params)
        self.dimensions = None
        # self.update_states()
        self.select_data()
        
    @param.depends('plot_type', watch=True)
    def update_defaults(self):
        if self.plot_type == 'Bar':
            self.aggregation = 'Daily'
            self.quantity = 'Confirmed'
            self.groupby = 'Global'
        else:
            self.aggregation = 'Totals'
            self.quantity = 'All'
            
    # def update_states(self):
    #     self.param.states.objects = sorted(data.where(data.Country == 'US', drop=True).Province_State.values)
    #     if not self.states:
    #         self.states = self.param.states.objects[:1]
    
    @param.depends('groupby', 'aggregation', 'quantity', 'countries', 'plot_type', watch=True)
    def select_data(self):
        kdims = ['Date', 'Quantity', 'Aggregation']
        self.dimensions = ['Date']
        select_kwargs = dict(Aggregation=self.aggregation)
        self.param.countries.precedence = -1
        # self.param.states.precedence = -1
        
        if self.groupby == 'Global':
            grouped_data = data.sum('Country')
        elif self.groupby == 'Country':
            grouped_data = data
            kdims.append('Country')
            self.param.countries.precedence = 1
            if len(self.countries) > 1 or self.plot_type == 'Curve':
                self.dimensions.append('Country')
            select_kwargs['Country'] = self.countries
#         elif self.groupby == 'State':
#             grouped_data = data.where(data.Country == 'US', drop=True).groupby('Province_State').sum('Region')
#             kdims.append('Province_State')
#             if len(self.states) > 1 or self.plot_type == 'Curve':
#                 self.dimensions.append('Province_State')
#             select_kwargs['Province_State'] = self.states
# #             self.param.countries.precedence = 1
#             self.param.states.precedence = 1
        
        if self.quantity == 'All':
            self.dimensions.append('Quantity')
        else:
            select_kwargs['Quantity'] = self.quantity
            
        selected_data = hv.Dataset(grouped_data, kdims=kdims, vdims=['counts']).select(**select_kwargs).aggregate(dimensions=self.dimensions, function=np.sum)
        self.selected_data = selected_data
    
    @param.depends('selected_data')
    def curves(self):
        curves = self.selected_data.to(hv.Curve, 'Date', ).options(tools=['hover'], show_grid=True)
        overlay = list()
        if self.quantity == 'All':
            overlay.append('Quantity')
        if self.groupby == 'Country':
            overlay.append('Country')
        if self.groupby == 'State':
            overlay.append('Province_State')
            
        if overlay:
            curves = curves.overlay(overlay).options(legend_position='top_left', )
        return curves.options(
                responsive=True,
                height=800,
                xrotation=60,
            )
    
    @param.depends('selected_data')
    def bars(self):
        kdims = self.dimensions
        return hv.Bars(self.selected_data, kdims=kdims).opts(
            responsive=True,
            height=800,
            stacked=False, 
            show_legend=False, 
            xrotation=60,
            tools=['hover'],
        )
    
    @param.depends('plot_type')
    def plot(self):
        return dict(
            Bar=self.bars,
            Curve=self.curves,
        )[self.plot_type]
    
    def panel(self):
        return pn.Row(
            pn.Param(self,
                     widgets={
                         'countries': {'height': 550},
                         # 'states': {'height': 550}
                     },
                     show_name=False),
            self.plot,
        )
