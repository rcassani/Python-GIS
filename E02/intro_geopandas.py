#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intro to geopandas
Read and Write shapefiles
"""

import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from fiona.crs import from_epsg

#%% Read shapefile with geopandas
filepath = '../data/damselfish_distributions/DAMSELFISH_distributions.shp'
data = gpd.read_file(filepath)

# Data is the world distribution of the Damselfish, for 30 species.
# The values for the Polygons are given in degrees (coordinates)
# World Geodetic System WGS84 or EPSG:4326 
# +x East
# -x West
# +y North
# -y South
# geometries in shapefile are stored in the 'geometry' field in the dataframe

# Get list of damselfish species
species = data.BINOMIAL.unique()

# Plot all species
data.plot(column='BINOMIAL', categorical=True, legend=True, cmap='tab20c')

# Plot top-5 species
# Counting instances per specie
count_spacies = data['BINOMIAL'].value_counts(dropna=False)
# Get top-5 species by number of instances 
top_5 = count_spacies.index.to_list()[0:5]
data_top5 = data[data.BINOMIAL.isin(top_5)]
data_top5.plot(column='BINOMIAL', categorical=True, legend=True)
    
##%% Write geometries to a shapefile with geopandas
# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()
newdata['geometry'] = None
# Coordinates of the Helsinki Senate square in Decimal Degrees
coordinates = [(24.950899, 60.169158), 
               (24.953492, 60.169158), 
               (24.953510, 60.170104), 
               (24.950958, 60.169990)]
# Create a shapely polygon from the coordinate-tuple list
poly = Polygon(coordinates)
# Add to gfd  
newdata.loc[0, 'geometry'] = poly
newdata.loc[0, 'Location'] = 'Helsinki Senate'
newdata.plot()

#Determine the coordinate reference system (projection) CRS for GeoDataFrame
print(newdata.crs)  
# Set the GeoDataFrame's coordinate system to WGS84 (EPSG:4326)
newdata.set_crs(from_epsg(4326), inplace=True)
# Let's see how the crs definition looks like
newdata.crs
# Write the data into that Shapefile
outfp = r"./results/helsinki_senate.shp"
newdata.to_file(outfp)
