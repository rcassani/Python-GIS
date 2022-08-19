#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordiante Reference Systems
Map projections
    
World Geodetic System WGS84 or EPSG:4326: 

EPSG: 3035
Lambert Azimuthal Equal Area projection (LAEA), 
recommended projection by European Comission.
"""

import zipfile
import geopandas as gpd
from matplotlib import pyplot as plt

# Unzip data
data_filepath = '../data/europe_borders.zip'
with zipfile.ZipFile(data_filepath,'r') as zip_ref:
    zip_ref.extractall(data_filepath[:-4])

# Read shapefile
filepath = data_filepath[:-4] + '/Europe_borders.shp'
data = gpd.read_file(filepath)

# Current coordinate reference system
print('Current CRS: ' + str(data.crs)) #WGS84 == EPSG:4326

# One example of the content of the data, it seems to be latitude-longitude
item = data.iloc[0]

# Plot data with EPSG4326 (WGS84) projection
plt.figure()
plt.title("EPSG4326 (WGS84) projection")
ax = plt.gca()
data.plot(facecolor='gray', edgecolor='black', ax=ax)
ax.set_xlabel('deg')
ax.set_ylabel('deg')

# Change CRS to EPSG: 3035
data_proj = data.copy()
data_proj.to_crs(epsg=3035, inplace=(True))
print('Current CRS: ' +  str(data_proj.crs))

plt.figure()
plt.title("EPSG3035 projection")
ax = plt.gca()
data_proj.plot(facecolor='gray', edgecolor='black', ax=ax)
ax.set_xlabel('m')
ax.set_ylabel('m')

