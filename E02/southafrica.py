#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 1: Points to map
Task 2: How long distance individuals have travelled?
"""

import csv
import geopandas as gpd
from shapely.geometry import Point, LineString
from fiona.crs import from_epsg

# Task 1: Points to map 
# Read file as CSV
items = []
points = []

# The data has 81379 rows and consists of locations and times of 
# social media posts inside Kruger national park in South Africa
# Data is in epsg(4326)

with open('../data/southafrica_posts/some_posts.csv') as fin:
    reader = csv.reader(fin, skipinitialspace=True, delimiter=',')
    headers = next(reader)
    for row in reader:
        item={}
        for ix, element in enumerate(row):
            item[headers[ix]] = element
        item['coords'] = Point(float(item['lon']), float(item['lat']))
        points.append(item['coords'])
        items.append(item)

# Create GeoDataFrame from dictionary
geodf = gpd.GeoDataFrame(items)

# Rename coords as geometry
geodf = geodf.rename(columns={'coords':'geometry'})
geodf.set_geometry(col='geometry', inplace=True)

# Add CRS
geodf.set_crs(from_epsg(4326), inplace=True)

# Plot
geodf.plot()

# Save shapely
outfp = r"./results/geo_poly.shp"
geodf.to_file(outfp)

# Task 2: How long distance individuals have travelled? 
# Data is projected to EPSG:32735 projection which stands for 
# UTM Zone 35S (UTM zone for South Africa) to transform the data into 
# metric system.

# List of unique users
users = geodf['userid'].unique()

# Project to EPSG:32735
geo_sa = geodf.copy()

# Define index
geo_sa = geo_sa.set_index('userid')

# For each user
trips = []
for user in users:
    # Find all points of that user
    geo_sa_user = geo_sa.loc[user]
    # If only one point do not calculate distance
    if len(geo_sa_user.shape) < 2:
        continue
    # Sort by datetime
    geo_sa_user = geo_sa_user.sort_values(by='timestamp')
    # n_trips 
    n_trips = len(geo_sa_user)-1
    for ix_trip in range(n_trips):
        trip={}
        trip['userid'] = user
        trip['timestamp_ini'] = geo_sa_user.iloc[ix_trip]['timestamp']
        trip['timestamp_fin'] = geo_sa_user.iloc[ix_trip+1]['timestamp']
        trip['geometry'] = LineString([geo_sa_user.iloc[ix_trip]['geometry'], 
                                       geo_sa_user.iloc[ix_trip+1]['geometry']])
        trips.append(trip)
  
movs = gpd.GeoDataFrame(trips)
# Add CRS
movs.set_crs(from_epsg(4326), inplace=True)
movs = movs.to_crs(epsg=32735)
movs['distance'] = movs['geometry'].length

# What was the shortest distance travelled (between two posts) in meters?
print('Shortest distance travelled (between two posts) was {0} meters'.format(
    movs['distance'].min()))
# What was the mean distance travelled (between two posts) in meters?
print('Mean distance travelled (between two posts) was {0} meters'.format(
    movs['distance'].mean()))
# What was the maximum distance travelled (between two posts) in meters?
print('Maximum distance travelled (between two posts) was {0} meters'.format(
    movs['distance'].max()))
# Plot all trips
movs.plot()