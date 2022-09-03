#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data from OpenStreetMap using the OSMnx package
More examples of OSMnx in https://github.com/gboeing/osmnx
"""

import osmnx as ox
import matplotlib.pyplot as plt

place_name = "Kamppi, Helsinki, Finland"
graph = ox.graph_from_place(place_name)

type(graph)
# Type MultiDiGraph stores nodes and edges with optional data or attribs

# Plotting DiGraph
fig, ax = ox.plot_graph(graph, node_color='#0000FF', edge_color='#FF0000')

# Getting graph data to GDF
# Area as GeoDataFrame
area = ox.geocode_to_gdf(place_name)                            
# Parks as GDF
parks = ox.geometries_from_place(place_name, tags={'leisure':'park'}) 
# Nodes and edges as GDF
nodes, edges = ox.graph_to_gdfs(graph)            

# plotting data
fig, ax = plt.subplots()
area.plot(ax=ax, facecolor='#000000')
edges.plot(ax=ax, linewidth=1, edgecolor='#AAAAAA')
nodes.plot(ax=ax, linewidth=1, edgecolor='#0000FF')
parks.plot(ax=ax, facecolor='#00FF00', alpha=0.7)
edges[edges['highway']=='footway'].plot(ax=ax, linewidth=1, edgecolor='#FF0000')
plt.axis('on')
plt.title('Data from Kamppi, Helsinki, Finland.  (OpenStreetMap)')
ax.set_xlabel('longitude (deg)')
ax.set_ylabel('latitude (deg)')