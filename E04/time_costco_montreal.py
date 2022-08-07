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
import openrouteservice as ors


# Unzip data
data_filepath = '../data/greater_montreal.zip'
with zipfile.ZipFile(data_filepath,'r') as zip_ref:
    zip_ref.extractall(data_filepath[:-4])

# Projection for Montreal: https://epsg.io/32198
mtl_epsg = 32188

# File with addresses
filepath = r'../data/costco_greater_montreal.txt'
costcos_gdf = gpd.GeoDataFrame(pd.read_csv(filepath, sep=',', skipinitialspace=True, index_col=False))

#%% Geocoding
# Geocode addresses (photon uses OSM)
geocode_gdf = gpd.tools.geocode(costcos_gdf['address'], provider='photon', user_agent='geocode-rcassani') 
# Join GDF
costcos_gdf = costcos_gdf.join(geocode_gdf['geometry'])
# Set CRS OpenStreetMap uses WGS84 (EPSG:4326)
costcos_gdf.to_crs(epsg=4326, inplace=(True))
# If address was not geocoded, use coordinates in file
costcos_gdf['geocoded'] = ~costcos_gdf['geometry'][:].is_empty
for ix in costcos_gdf[~costcos_gdf['geocoded']].index.to_list():
    costcos_gdf.at[ix, 'geometry'] = Point(float(costcos_gdf.at[ix, 'longitude']), float(costcos_gdf.at[ix, 'latitude']))

# TEST plot with background map
# ax = costcos_gdf.plot(facecolor='blue')
# for x, y, label in zip(costcos_gdf.geometry.x, costcos_gdf.geometry.y, costcos_gdf.name):
#     ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
# # Add background map
# cx.add_basemap(ax, crs=costcos_gdf.crs) 

#%% Obtain the isochrones for each Costco location with OpenRouteService
client = ors.Client(key='')

isos_gdfs = []
lens_isos = np.zeros(len(costcos_gdf))
for ix, costco in costcos_gdf.iterrows():
    print('Isochrones for ' + costco['name'])
    coordinate = [[costco['geometry'].x, costco['geometry'].y]]
    # Query for Isochrone, it results a GeoJSON
    iso = client.isochrones(locations=coordinate,
                            range_type='time',
                            profile='driving-car',
                            range=[2400],
                            validate=False,
                            interval=300,
                            attributes=['total_pop'])
    # GeoJSON to GDF
    iso_gdf = gpd.GeoDataFrame.from_features(iso)
    # Number of isochrones
    lens_isos[ix] = len(iso_gdf)
    # Set CRS OpenRouteService uses WGS84 (EPSG:4326)      
    iso_gdf.set_crs('epsg:4326', inplace=True)
    # Add name column
    iso_gdf['name'] = costco['name']
    iso_gdf['group_index'] = ix
    isos_gdfs.append(iso_gdf)        

# Verify that all the costcos have the same number of isochrones
ns_isos, count = np.unique(lens_isos, return_counts=True)
if count == len(costcos_gdf):
    n_isos = ns_isos[0]
else:
    print('All points must have the same number of isochrones')
    exit()
    
# Concatenate isochrones
isos_gdf = pd.concat(isos_gdfs)
# Transfor to crs=mtl_epsg
isos_gdf.to_crs(epsg=mtl_epsg, inplace=(True))
costcos_gdf.to_crs(epsg=mtl_epsg, inplace=(True))

#%% Load Montreal shapefiles
# Rectangle ancompassing the Greater Montreal Area (GMA)
gma_gdf = gpd.read_file('../data/greater_montreal/rect.shp')
gma_gdf.to_crs(epsg=mtl_epsg, inplace=(True))
# Water bodies in the the GMA rectangle
wtr_gdf = gpd.read_file('../data/greater_montreal/water_mtl.shp')
wtr_gdf.to_crs(epsg=mtl_epsg, inplace=(True))

# TEST Add background map
# ax = gma_gdf.plot(edgecolor='blue', facecolor='none')
# costcos_gdf.plot(facecolor='blue', ax = ax)
# cx.add_basemap(ax, crs=gma_gdf.crs) 

#%% Create grid 
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

grido  = grid.copy()

#%% Find the time to each Costco for each point in the grid
def isCenterInPolygon(polygon1, polygon2):
    return polygon1.centroid.within(polygon2)

iso_costcos_labels = []
for ix, costco in costcos_gdf.iterrows():
    print('Testing isochrones for ' + costco['name'])    
    # Each grid point has a value iso_costco_XX with XX = costco index
    iso_costcos_label = 'iso_costco_' + '{:02}'.format(ix)
    iso_costcos_labels.append(iso_costcos_label)
    # iso_costco_XX = N+1 with N = len(isochrones)
    grido[iso_costcos_label] = n_isos + 1
    # Sort isos from longer to shorter, and re-index
    iso_gdf = isos_gdf[isos_gdf['name'] == costco['name']].sort_values(by='value', ascending=False, ignore_index=True)
    for ic, iso in iso_gdf.iterrows():        
        tmp = grido['geometry'].apply(isCenterInPolygon, polygon2=iso['geometry']).astype(int)
        grido[iso_costcos_label] = grido[iso_costcos_label] - tmp

# Find minimum isochrone
grido['iso_costco_min'] = grido[iso_costcos_labels].min(axis=1)    

#%% Plotting by iso_costco_min
# Costco logo, from https://seekvectors.com/post/costco-icon
costco_marker = parse_path("""M995.1,61.2c-84.7-24.8-180.9-38-276.7-38C376.8,23.2,
                   66.8,239,12.7,508.6c-52.6,263.5,166.2,468.2,498.4,468.2
                   c75.7,0,235.2-11,308.7-36.8l81.4-345.7c-78.5,52.7-162.4,
                   85.8-259.7,85.8c-126.7,0-220.8-78.4-200.5-180.2
	               C461,399.5,580.4,319.9,707.1,319.9c95.8,0,172.2,42.9,230.2,92.8L995.1,61.2z""")
costco_marker = costco_marker.transformed(mpl.transforms.Affine2D().scale(1,-1))

ax = grido.plot(column="iso_costco_min", cmap="viridis_r", linewidth=0, categorical=True, legend=True, alpha=0.8, zorder=2)
cx.add_basemap(ax, crs=grido.crs, source=cx.providers.Stamen.TonerBackground, zorder=1)
wtr_gdf.plot(edgecolor='none', facecolor='#AAAAAA', zorder=3, ax=ax)
cx.add_basemap(ax, crs=grido.crs, source=cx.providers.Stamen.TonerLabels, zorder=4)
ax.set_title('Driving time to closest Costco (minutes)')
costcos_gdf.plot(facecolor='#E21D39', edgecolor='k', ax=ax, marker=costco_marker, markersize=500, zorder=5)
costcos_gdf.plot(color='black', ax=ax, markersize=10, zorder=5)
for x, y, label in zip(costcos_gdf.geometry.x, costcos_gdf.geometry.y, costcos_gdf.name):
    ax.annotate(label, xy=(x, y), xytext=(14, -10), textcoords="offset points", zorder=5)
ax.set_xlim((x_min, x_max))
ax.set_ylim((y_min, y_max))
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)

# Replace categorical legends with custom legends
# https://stackoverflow.com/a/66212945/4859684               
clusdict={1.0: ' 0 -  5 min', 2.0: ' 5 - 10 min', 3.0: '10 - 15 min', 
          4.0: '15 - 20 min', 5.0: '20 - 25 min', 6.0: '25 - 30 min', 
          7.0: '30 - 35 min', 8.0: '35 - 40 min', 9.0: '40 +    min'}
 
def replace_legend_items(legend, mapping):
    for txt in legend.texts:
        for k,v in mapping.items():
            if txt.get_text() == str(k):
                txt.set_text(v)

replace_legend_items(ax.get_legend(), clusdict)
