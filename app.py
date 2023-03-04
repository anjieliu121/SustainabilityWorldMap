from shiny import App, render, ui, reactive
import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#import folium
#import geopandas
from pathlib import Path

import ipyleaflet as L
#from ipywidgets import HTML

from shinywidgets import output_widget, reactive_read, register_widget
from googlesearch import search

import geopandas as gpd


# remember to uninstall: ipyleaflet, ipywidgets, shinywidgets, google,
# beautifulsoup4 , lxml, html5lib




#from pathlib import Path

#sns.set_theme()
infile = Path(__file__).parent / "co2_emissions_kt_by_country.csv"
co2 = pd.read_csv(infile)
keys = list(co2.country_name.unique())
values = list(co2.country_name.unique())
d_country = { k:v for (k,v) in zip(keys, values) }


app_ui = ui.page_fluid(
    ui.h2("Hello Shiny!"),
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
    

    center = [20,0]
    zoom = 2
    m = L.Map(basemap=L.basemaps.CartoDB.Positron, center=center, zoom=zoom)
    m.add_control(L.leaflet.ScaleControl(position="bottomleft"))
    
    #highlight = L.GeoData(geo_dataframe = c, 
    #style={'color': 'green', 'fillColor': 'green'},
    #hover_style={'fillColor': 'green', 'fillOpacity': 1})

    #m.add_layer(highlight)

    
    
    # When the slider changes, update the map's zoom attribute (2)
    @reactive.Effect
    def _():
        m.zoom = input.zoom()

    # When zooming directly on the map, update the slider's value (2 and 3)
    @reactive.Effect
    def _():
        ui.update_slider("zoom", value=reactive_read(m, "zoom"))
    
    
    @reactive.Effect
    def _():
        center = [20,0]
        zoom = 2
        m = L.Map(basemap=L.basemaps.CartoDB.Positron, center=center, zoom=zoom)

        m.add_layer(L.Marker(location=(52.204793, 360.121558)))

        countries = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        c = countries[countries['name'] == input.country()]
        
        highlight = L.GeoData(geo_dataframe = c, style={'color': 'green', 'fillColor': 'green'},  hover_style={'fillColor': 'green', 'fillOpacity': 1})

        m.add_layer(highlight)
        register_widget("map", m)
        
        
    
    @output
    @render.text
    def txt():
        return f'Country: {input.country()}\tYears: {input.year()[0]}-{input.year()[1]}'
    
    @output
    @render.text
    def websites():
        phrase = f"{input.country()} {input.year()[0]} to {input.year()[1]} co2 emission"
        s = search(phrase, start=0, stop=5)
        o = ""
        for i in s:
            #ui.tags.link(i)
            o += i + "\n"
        return o
    
    @output
    @render.plot
    def plot():
        user = co2.loc[co2['country_name'].isin([input.country()])]
        user = user.loc[user['year'].isin(list(range(input.year()[0], input.year()[1]+1)))]
        fig, ax = plt.subplots()

        # make x-axis ticker all integers
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_locator(ticker.MaxNLocator(integer=True))
        fig = plt.plot(user.year, user.value)
        plt.title(f"CO2 Emission Over Years in {input.country()}")
        plt.xlabel("Year")
        plt.ylabel("CO2 Emission")
        return fig
    
    
    
    

   




app = App(app_ui, server)
