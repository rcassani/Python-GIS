#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocoding is converting addresses (24 Sussex Dr, Ottawa, ON K1M 1M4, Canada) 
into coordinates (45.444368, -75693835) or vice versa
"""

import pandas as pd
from geopandas.tools import geocode
import os

# File with addresses
filepath = r'../data/helsinki_addresses.txt'
data = pd.read_csv(filepath, sep=';')

# Geocode addresses with Nominatim backend
geo = geocode(data['addr'], provider='nominatim', user_agent='geocode-rcassani') 
# this geocode provider does not require API key, 
# but need a user_agent != "my-application"

# Retrieved coordinates
geo.loc[0]

# Join 'id' from data to geo 
join = geo.join(data['id'])

# Export the geometries to a shapefile
os.mkdir('results')
filepath_shp = r"./results/addresses.shp"
join.to_file(filepath_shp)

# Plot of the location of the addresses
join.plot()