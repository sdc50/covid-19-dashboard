import param
import panel as pn

from .covid_data import data, load_totals
from .covid_plotter import CovidPlotter
from .covid_mapper import CovidMapper

pn.extension()


class CovidSummary(param.Parameterized):
    @staticmethod
    def total_html(label, value, color):
        return f'<div style="background-color:{color}; display:inline-block; height: 100px; width: 300px; margin: 0 20px; color:white; padding-top: 20px;">' \
            f'<span style="display:block; text-align:center; font-size:20px; margin: 0 20px -10px 20px;">{label}</span>' \
            f'<span style="display:block; text-align:center; font-size:50px; margin: 0 20px;">{value:,}</span></div>'

    def panel(self):
        global_totals = data.sum('Country').sel(Aggregation='Totals')
        img = 'http://wp.sbcounty.gov/cao/countywire/wp-content/uploads/2020/03/banner.png'
        # confirmed_total = int(global_totals.sel(Quantity='Confirmed').isel(Date=-1)['counts'])
        # deaths_total = int(global_totals.sel(Quantity='Deaths').isel(Date=-1)['counts'].sum())
        # recovered_total = int(global_totals.sel(Quantity='Recovered').isel(Date=-1)['counts'])
        # active_total = int(global_totals.sel(Quantity='Active').isel(Date=-1)['counts'])
        # new_cases = confirmed_total - int(global_totals.sel(Quantity='Confirmed').isel(Date=-2)['counts'])
        today_totals, yesterday_totals = load_totals()
        new_totals = today_totals - yesterday_totals

        return pn.Column(
            pn.Row(
                pn.Spacer(width=120),
                pn.panel(img),
            ),
            pn.pane.HTML(
                '<div style="margin: 20px;">' +
                self.total_html('Total Confirmed', today_totals['Confirmed'], 'blue') +
                self.total_html('Total Active', today_totals['Active'], 'orange') +
                self.total_html('New', new_totals['Confirmed'], 'red') +
                '</div>',
                width=1500,
            ),
            pn.pane.HTML(
                '<div style="margin: 20px 200px;">' +
                self.total_html('Total Recovered', today_totals['Recovered'], 'green') +
                self.total_html('Total Deaths', today_totals['Deaths'], 'gray') +
                '</div>',
                width=1500,
            ),
        )


class CovidDashboard(param.Parameterized):
    summary = param.ClassSelector(CovidSummary, default=CovidSummary())
    plotter = param.ClassSelector(CovidPlotter, default=CovidPlotter())  # this doesn't work, not sure why
    mapper = param.ClassSelector(CovidMapper, default=CovidMapper())
    
    def panel(self):
        return pn.Tabs(
            ('Summary', self.summary_panel()),
            ('Map', self.mapper.panel()),
            ('Plots', self.plotter.panel()),
        )
