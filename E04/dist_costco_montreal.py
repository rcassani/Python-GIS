#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Where is the closest Costco in Montreal?
"""

import zipfile
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import contextily as cx
import matplotlib as mpl
from matplotlib_scalebar.scalebar import ScaleBar
from svgpath2mpl import parse_path
import folium

# Unzip data
data_filepath = '../data/greater_montreal.zip'
with zipfile.ZipFile(data_filepath,'r') as zip_ref:
    zip_ref.extractall(data_filepath[:-4])

# Projection for Montreal: https://epsg.io/32198
mtl_epsg = 32188

# File with addresses
filepath = r'../data/costco_greater_montreal.txt'
data_gdf = gpd.GeoDataFrame(pd.read_csv(filepath, sep=',', skipinitialspace=True, index_col=False))

#%% Geocoding  
# Geocode addresses (photon uses OSM)
geocode_gdf = gpd.tools.geocode(data_gdf['address'], provider='photon', user_agent='geocode-rcassani') 
# Join GDF
data_gdf = data_gdf.join(geocode_gdf['geometry'])
# Set CRS OpenStreetMap uses WGS84 (EPSG:4326)
data_gdf.to_crs(epsg=4326, inplace=(True))
# If address was not geocoded, use coordinates in file
data_gdf['geocoded'] = ~data_gdf['geometry'][:].is_empty
for ix in data_gdf[~data_gdf['geocoded']].index.to_list():
    data_gdf.at[ix, 'geometry'] = Point(float(data_gdf.at[ix, 'longitude']), float(data_gdf.at[ix, 'latitude']))
# Set CRS to EPSG:6622 NAD83(CSRS) / Quebec Lambert, given in meters
data_gdf.to_crs(epsg=mtl_epsg, inplace=(True))

# TEST plot with background map
# ax = data_gdf.plot(facecolor='blue')
# for x, y, label in zip(data_gdf.geometry.x, data_gdf.geometry.y, data_gdf.name):
#     ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
# # Add background map
# cx.add_basemap(ax, crs=data_gdf.crs) 

#%% Load shapefiles
# Rectangle ancompassing the Greater Montreal Area (GMA)
gma_gdf = gpd.read_file('../data/greater_montreal/rect.shp')
gma_gdf.to_crs(epsg=mtl_epsg, inplace=(True))
# Water bodies in the the GMA rectangle
wtr_gdf = gpd.read_file('../data/greater_montreal/water_mtl.shp')
wtr_gdf.to_crs(epsg=mtl_epsg, inplace=(True))

# TEST Add background map
# ax = gma_gdf.plot(edgecolor='blue', facecolor='none')
# data_gdf.plot(facecolor='blue', ax = ax)
# cx.add_basemap(ax, crs=gma_gdf.crs) 

#%% Compute ditance grid
# Area for map, rounded to closest kilometer
bounds = gma_gdf.loc[0]['geometry'].bounds
x_min = np.floor(bounds[0] / 1000) * 1000
x_max = np.ceil(bounds[2]  / 1000) * 1000
y_min = np.floor(bounds[1] / 1000) * 1000
y_max = np.ceil(bounds[3]  / 1000) * 1000

# Create array of square polygons
polygon_grid = []
polygon_side = 1000 # meters
for x in np.arange(x_min, x_max, polygon_side):
    for y in np.arange(y_min, y_max, polygon_side):
        new_polygon  = {}
        coordinates = [(x,              y), 
                       (x+polygon_side, y), 
                       (x+polygon_side, y+polygon_side), 
                       (x,              y+polygon_side),
                       (x,              y)]
        new_polygon['geometry'] = Polygon(coordinates)               
        polygon_grid.append(new_polygon)
grid = gpd.GeoDataFrame(data=polygon_grid, crs=mtl_epsg)
grid['index_col'] = grid.index
# Remove water bodies
grid = grid.overlay(wtr_gdf, how='difference')

#%% Compute distance for each polygon centroid to every data point
def distance(point, polygon):
    # Distance from a point to the centroid of a polygon
    return point.distance(polygon.centroid)

dist_labels = []
for data_ix, data_point in zip(data_gdf.index, data_gdf['geometry']):   
    dist_label = 'dist' + '{:02}'.format(data_ix)
    dist_labels.append(dist_label)
    grid[dist_label] = grid['geometry'].apply(distance, args=(data_point,))   

# Find minimum distance
grid['dist_min'] = grid[dist_labels].min(axis=1)
grid['dist_min_km'] = grid['dist_min'] / 1000


#%% Plotting by distance
# Costco logo, from https://seekvectors.com/post/costco-icon
costco_marker = parse_path("""M995.1,61.2c-84.7-24.8-180.9-38-276.7-38C376.8,23.2,
                   66.8,239,12.7,508.6c-52.6,263.5,166.2,468.2,498.4,468.2
                   c75.7,0,235.2-11,308.7-36.8l81.4-345.7c-78.5,52.7-162.4,
                   85.8-259.7,85.8c-126.7,0-220.8-78.4-200.5-180.2
	               C461,399.5,580.4,319.9,707.1,319.9c95.8,0,172.2,42.9,230.2,92.8L995.1,61.2z""")
costco_marker = costco_marker.transformed(mpl.transforms.Affine2D().scale(1,-1))

ax = grid.plot(column="dist_min_km", cmap="viridis_r", linewidth=0, scheme="userdefined", 
                classification_kwds={'bins':[5, 10, 15, 20, 25, 35, 55]}, legend=True, alpha=0.5, zorder=2)
cx.add_basemap(ax, crs=grid.crs, source=cx.providers.Stamen.TonerBackground, zorder=1)
cx.add_basemap(ax, crs=grid.crs, source=cx.providers.Stamen.TonerLabels, zorder=4)
ax.set_title('Distance to closest Costco (km)')
data_gdf.plot(facecolor='#E21D39', edgecolor='k', ax=ax, marker=costco_marker, markersize=500, zorder=5)
data_gdf.plot(color='black', ax=ax, markersize=10, zorder=5)
for x, y, label in zip(data_gdf.geometry.x, data_gdf.geometry.y, data_gdf.name):
    ax.annotate(label, xy=(x, y), xytext=(14, -10), textcoords="offset points", zorder=5)
ax.set_xlim((x_min, x_max))
ax.set_ylim((y_min, y_max))
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)

#%% Interactive map
m = folium.Map(location=[45.5765, -73.6276], zoom_start=11, tiles='cartodbpositron')

folium.Choropleth(
    geo_data=grid,
    data=grid,
    columns=['index_col','dist_min_km'],
    popup=folium.Popup("feature.properties.index_col"),
    key_on='feature.properties.index_col',
    fill_color='YlGnBu',
    fill_opacity=0.5,
    line_weight=0,
    legend_name='Distance to closest Costco (km)',
).add_to(m)

for ix, item in data_gdf.iterrows():
    folium.Marker([item.latitude, item.longitude], 
                  popup=item['name'],
                  tooltip=item['name'],
                  icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')).add_to(m)

m.save("dist_costco_montreal.html")