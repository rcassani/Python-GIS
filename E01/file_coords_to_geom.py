#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reading coordinates from a CSV file and creating shapefile geometries
"""

import csv
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import transform
import pyproj

# Coordinate Reference System
epsg_4326 = pyproj.CRS('EPSG:4326')
epsg_3035 = pyproj.CRS('EPSG:3035')
# EPSG:3035 = Lambert Azimuthal Equal Area projection (LAEA),
# recommended projection by European Comission.
# Projection
project = pyproj.Transformer.from_crs(epsg_4326, epsg_3035, always_xy=True).transform

# Origin and Destination points are given in degrees (EPSG:4326 aka WGS84)
# Read file as CSV but ; rather than ,
items = []
with open('../data/travelTimes_2015_Helsinki.txt') as fin:
  reader = csv.reader(fin, skipinitialspace=True, delimiter=';')
  headers = next(reader)
  for row in reader:
    item={}
    for ix, element in enumerate(row):
      item[headers[ix]] = element
      items.append(item)

# Create lists of points and lines
distances = []

# Create geometries for each trip
for item in items:
   # Origin and Destination points are given in degrees (EPSG:4326 aka WGS84)
   orig_point_deg = Point(float(item['from_x']), float(item['from_y']))
   dest_point_deg = Point(float(item['to_x']), float(item['to_y']))
   # Project Points to have them in meters
   orig_point_m = transform(project, orig_point_deg)
   dest_point_m = transform(project, dest_point_deg)
   line = LineString([orig_point_m, dest_point_m])
   distances.append(line.length)

distances = np.array(distances) # in meters
mean_dist = np.mean(distances)
print('The average Euclidean distance between points was: {0:.2f} km'.format(mean_dist/1000))
