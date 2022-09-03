#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reclassification
"""

import zipfile
import geopandas as gpd
from shapely.geometry import Polygon
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar

# Unzip data
data_filepath = '../data/helsinki_region_travel_time_2015.zip'
with zipfile.ZipFile(data_filepath,'r') as zip_ref:
    zip_ref.extractall(data_filepath[:-4])

# File with square poligons, each of them is assignated with a travel time 
# from it to the loacation id = 5975375
# Description of the other fields here: 
# https://blogs.helsinki.fi/accessibility/helsinki-region-travel-time-matrix-2015/
  
fiepath = data_filepath[:-4] + '/data/TravelTimes_to_5975375_RailwayStation.shp'
acc = gpd.read_file(fiepath)

# Where is location id = 5975375?
# Coordinates in km in EPSG: 3067 (From MetropAccess_YKR_grid.zip in above URL)
point = {}
coordinates = [(386000.0001386078,  6672000.000132944), 
               (385750.0001386631,  6672000.000132954), 
               (385750.00013865647, 6672250.000132906), 
               (386000.00013860187, 6672250.0001329), 
               (386000.0001386078,  6672000.000132944)]
# Create polygon from coordinates
point['id'] = 5975375
point['geometry'] = Polygon(coordinates)
geodf = gpd.GeoDataFrame(data=point, index=[0], crs=3067)
centroid = geodf[geodf['id']== 5975375]['geometry'].centroid
# To EPSG:4326
print('Longitude {0:.2f} deg, Latitude {1:.2f} deg'.format(centroid.to_crs(4326)[0].x, centroid.to_crs(4326)[0].y))
# The center of the polygon is near the Ateneum 
# (Museum of Finnish and international art)
# Kaivokatu 2, 00100 Helsinki, Finland

# The NoData values are presented with value -1
# Keep only valid data
# pt_r_tt Public transportation travel time, including time before starting the travel (minutes)
# walk_d Walking distance (meters)
acc['walk_d_km'] = acc['walk_d'] / 1000
acc = acc[(acc['pt_r_tt'] >=0) & (acc['walk_d_km'] >=0)]

# To accelearate the plotting time:
# Keep only the closest 20% of the data
acc = acc.sort_values(by=['walk_d_km'])
n_rows = len(acc)
acc = acc.iloc[0 : n_rows // 5, : ]

# Plotting PT travel times
ax = acc.plot(column="pt_r_tt", k=9, cmap="RdYlBu", linewidth=0, scheme="Fisher_Jenks", legend=True, alpha=0.5,)
ax.set_title('Public transportation times (min)')
geodf.geometry.centroid.plot(ax=ax, markersize=5, color='k', zorder=10)
cx.add_basemap(ax, crs=acc.crs)
# Scale bar
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)
ax.axis('off')

# Plotting by distance
ax = acc.plot(column="walk_d_km", k=9, cmap="RdYlBu", linewidth=0, scheme="Fisher_Jenks", legend=True, alpha=0.5,)
ax.set_title('Walking distance (km)')
geodf.geometry.centroid.plot(ax=ax, markersize=5, color='k', zorder=10)
cx.add_basemap(ax, crs=acc.crs)
# Scale bar
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)
ax.axis('off')

# Classify travel times into classes
# Natural Break classification: 
# http://wiki.gis.com/wiki/index.php/Jenks_Natural_Breaks_Classification
n_classes = 5
ax = acc.plot(column='pt_r_tt', linewidth=0, scheme='natural_breaks', k=n_classes, 
              cmap='viridis', edgecolor='k', alpha=0.5, legend=True)
ax.set_title('Public transportation times (min):' + str(n_classes) + ' classes')
geodf.geometry.centroid.plot(ax=ax, markersize=5, color='k', zorder=10)
cx.add_basemap(ax, crs=acc.crs)
# Scale bar
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)
ax.axis('off')

# Classify travel distance into classes
ax = acc.plot(column='walk_d_km', linewidth=0, scheme='natural_breaks', k=n_classes, 
              cmap='viridis', edgecolor='k', alpha=0.5, legend=True)
ax.set_title('Waling distance (km): ' + str(n_classes) + ' classes')
geodf.geometry.centroid.plot(ax=ax, markersize=5, color='k', zorder=10)
cx.add_basemap(ax, crs=acc.crs)
# Scale bar
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)
ax.axis('off')

# Customized binary classification
# Find places that are less than 35 min in public transportation AND further than 5 km
def custom_classifier(row, col1, col2, thr1, thr2, col_out):
    if row[col1] < thr1 and row[col2] > thr2:
      row[col_out] = 'Yes'
    else:
      row[col_out] = 'No'
    return row

# Creates column for custom_classifier
acc['custom_place'] = None
acc = acc.apply(custom_classifier, col1='pt_r_tt', col2='walk_d_km', thr1=35, thr2=5, col_out='custom_classifier', axis=1)
ax = acc.plot(column='custom_classifier', linewidth=0, legend=True, categorical=True, cmap='viridis', alpha=0.5)
ax.set_title('Places with PT times < 35 min AND more than 5 km away')
geodf.geometry.centroid.plot(ax=ax, markersize=5, color='k', zorder=10)
cx.add_basemap(ax, crs=acc.crs)
# Scale bar
scale_bar = ScaleBar(dx=1, location='lower right')
ax.add_artist(scale_bar)
ax.axis('off')
