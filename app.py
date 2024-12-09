# imports

# website
from shiny import App, render, ui, reactive
# dataframe
import pandas as pd
# plots
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# directory
from pathlib import Path
# map
import ipyleaflet as L
# interactive map
from shinywidgets import output_widget, reactive_read, register_widget
# google search
from googlesearch import search
# geostats
import geopandas as gpd


# remember to uninstall: ipyleaflet, ipywidgets, shinywidgets, google,
# beautifulsoup4 , lxml, html5lib


# import dataset
infile = Path(__file__).parent / "co2_emissions_kt_by_country.csv"
co2 = pd.read_csv(infile)
# dictionary for country selection bar
keys = list(co2.country_name.unique())
values = list(co2.country_name.unique())
d_country = { k:v for (k,v) in zip(keys, values) }


# user interactive
app_ui = ui.page_fluid(
    ui.h2("Sustainability Map!"),
    ui.row(
        ui.column(
            6,
            ui.div(
                {"class": "app-col"},
            ),
            ui.input_select("country", "Select a Country", d_country),
            ui.input_slider("year", "Select Year Range", min=1960, max=2019, value=(1960, 2019)),
            ui.output_text_verbatim("txt"),
            ui.output_plot("plot", height="500px", width="500px"),
        ),
        ui.column(
            6,
            ui.div(
                ui.input_slider("co2emission", "Select CO2 Emission", min=0, max=13000000, value=8000000),
                ui.input_slider("co2year", "Select a Year", min=1960, max=2019, value=2019),
                ui.input_slider("zoom", "Map zoom level", min=1, max=18, value=1),
                ui.output_ui("map_bounds"),
            ),
            output_widget("map"),
        ),
    ),
    ui.row(
        ui.h4("Check out why this country has such CO2 emission:"),
        ui.tags.link(ui.output_text_verbatim("websites")),
        
    )
    
    
)



def server(input, output, session):
    '''
    _()
    packages: ipyleaflet, geopandas, pandas, shinywidgets
    user input: country name, year, CO2 emission amount, zoom-in ratio
    web output: 
        - zoom in and out according to user-selected ratio
        - highlight the user-selected country in green
        - highlight the countries that are below the user-selected CO2 emission amount
    '''
    @reactive.Effect
    def _():
        # create the map
        center = [20,0]
        zoom = 1
        m = L.Map(basemap=L.basemaps.CartoDB.Positron, center=center, zoom=zoom)
        m.add_control(L.leaflet.ScaleControl(position="bottomleft"))
        
        # When the slider changes, update the map's zoom attribute
        m.zoom = input.zoom()
        # When zooming directly on the map, update the slider's value
        ui.update_slider("zoom", value=reactive_read(m, "zoom"))
        
        # country geography data dataframe
        countries = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')

        # subset countries for the user-selected country
        c = countries[countries['NAME'] == input.country()]
        # highlight selected country in purple
        highlight = L.GeoData(geo_dataframe = c, style={'color': 'purple', 'fillColor': 'purple'},  hover_style={'fillColor': 'purple', 'fillOpacity': 1})
        m.add_layer(highlight)
        
        # select "green" countries
        greencountries = []
        names = set(countries['ISO_A3']) & set(co2.country_code)
        for code in names:
            user = co2[co2.country_code == code]
            user = user[user.year == input.co2year()]
            if len(user.value.values) > 0:
                if (user.value.values[0]) <= float(input.co2emission()):
                    greencountries.append(code)
        # subset all "green" countries
        allgreenc = countries.loc[countries['ISO_A3'].isin(greencountries)]
        # highlight those countries in green
        greenc = L.GeoData(geo_dataframe = allgreenc, style={'color': 'green', 'fillColor': 'green'}, hover_style={'fillColor': 'green', 'fillOpacity': 1})
        m.add_layer(greenc)
        
        register_widget("map", m)
    
    '''
    txt()
    packages: N/A
    user input: country name, year interval
    web output: display user selected country and year interval
    '''
    @output
    @render.text
    def txt():
        return f'Country: {input.country()}\tYears: {input.year()[0]}-{input.year()[1]}'
    
    '''
    websites()
    packages: google, beautifulsoup4
    user input: country name, year interval
    web output: display top 5 Google search result related to the CO2 emission of the selected country within the year intervval
    '''
    @output
    @render.text
    def websites():
        phrase = f"{input.country()} {input.year()[0]} to {input.year()[1]} CO2 emission"
        s = search(phrase, num_results=5)
        o = f"Search \"{phrase}\" on Google:\n"
        for i in s:
            o += i + "\n"
        return o
    
    
    '''
    plot()
    packages: matplotlib
    user input: country name, year interval
    web output: display a line plot of the changes of CO2 values over selected years in a given country
    '''
    @output
    @render.plot
    def plot():
        user = co2.loc[co2['country_name'].isin([input.country()])]
        user = user.loc[user['year'].isin(list(range(input.year()[0], input.year()[1]+1)))]
        fig, ax = plt.subplots()

        # make x-axis ticker all integers
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_locator(ticker.MaxNLocator(integer=True))
        # plot
        fig = plt.plot(user.year, user.value)
        plt.title(f"CO2 Emission Over Years in {input.country()}")
        plt.xlabel("Year")
        plt.ylabel("CO2 Emission")
        return fig
    
    
    
    

   




app = App(app_ui, server)
