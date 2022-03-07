# GIS with Python
This repo is to host a [gallery](#Gallery) with examples and exercies that I have found useful at exploring the use of Python in GIS applications.
It also provides a list of [resources](#Resources) that have helped me.

## Environment setup
My setup is carried out with [`conda`](https://docs.conda.io/en/latest/).

The [`gis.yml`](gis.yml) file is a conda environment with all the required packages.
```
$ conda env create -f ./gis.yml
```

If it fails to create the enviroment, it can be replicated with:
```
$ conda env create --name gis
$ conda config --env --add channels conda-forge
$ conda config --env --set channel_priority strict
$ conda install python=3 geopands geopy osmnx
```

Once the setup is done a new `.yml` can be created to reproduce the environment
```
conda env export --nbame gis > ./gis.yml
```

## Gallery
| Dir | Topic  | From  |
|---|---|---|
| E01 | Create [shapefile](https://en.wikipedia.org/wiki/Shapefile) geometries with [shapely](https://pypi.org/project/Shapely/) | [1]|
| E02  | Intro to [GeoPandas](https://geopandas.org/en/stable/) and [CRSs](https://en.wikipedia.org/wiki/Spatial_reference_system)   | [1]  |
| E03  |   |   |

 [E1],  SUBJ , From [1]


# Resources  
[1] Introduction to Python GIS [https://automating-gis-processes.github.io/CSC18/index.html](https://automating-gis-processes.github.io/CSC18/index.html)
