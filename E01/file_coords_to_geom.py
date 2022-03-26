#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reading coordinates from a CSV file and creating shapefile geometries
"""

import csv
import numpy as np
from shapely.geometry import Point, LineString

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
orig_points = []
dest_points = []
lines = []
distances = []

for item in items:
   orig_point = Point(float(item['from_x']), float(item['from_y'])) 
   orig_points.append(orig_point)
   dest_point = Point(float(item['to_x']), float(item['to_y']))
   dest_points.append(dest_point)
   line = LineString([orig_point, dest_point]) 
   lines.append(line)
   distances.append(line.length)
   
distances = np.array(distances) # in meters
mean_dist = np.mean(distances)
print('The mean Euclidian (x-y plane) distance was: {0} degrees'.format(mean_dist))
print('These are NOT degrees for the "great-circle distance"')
# To have the units in meters, this has to be projected to a
# Spatial Reference System (SRS) or 
# Coordinate Reference System (CRS) or
# Coordiante System (CS)
