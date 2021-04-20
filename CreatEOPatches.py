#!/usr/bin/env python
# Default libs
import sys
import os

# Data visualisation/Datetime
import numpy as np
import datetime

# Basics of GIS
import geopandas as gpd
from shapely.geometry import Polygon

# Sentinel Hub libs
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

# import custom scripts
from general_functions import makepath
from secrets import INSTANCE_ID, CLIENT_ID, CLIENT_SECRET

# Load folders
geospatialFolder = r'.\bbox'

# Credentials and authorisation     
INSTANCE_ID = INSTANCE_ID
CLIENT_ID = CLIENT_ID
CLIENT_SECRET = CLIENT_SECRET

config = SHConfig()
try:
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID: 
        config.instance_id = INSTANCE_ID
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
except:
    if config.sh_client_id == '' & config.sh_client_secret == '' & config.instance_id == '': 
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")

def createGeoJson(geospatialFolder, filename):
    
    AOI = os.path.join(geospatialFolder, filename)   
    # Load boundaries of the AOI in GeoJson format
    country = gpd.read_file(AOI) # Lithuania tile

    # Transform GeoJSON projection and find the dimensions 
    country_crs = CRS.UTM_34N # for Lithuania for Cyprus is 36N
    country = country.to_crs(crs={'init': CRS.ogc_string(country_crs)})
    
    # Get the country's shape in polygon format
    country_shape = country.geometry.values[-1]
    return country, country_shape

def patchesGenerator(input_folder, outputname, patches = 24000):  
    country, country_shape = createGeoJson(input_folder, 'LithAOI.json')     
    shapefile_name = f'{outputname}.gpkg'
    shapefile_fullpath = os.path.join(input_folder,shapefile_name)  
    
    # Create the splitter to obtain a list of bboxes
    bbox_splitter = UtmZoneSplitter([country_shape], country.crs, patches) # 35 patches per S2 image tile 
    bbox_list = np.array(bbox_splitter.get_bbox_list())
    info_list = np.array(bbox_splitter.get_info_list())   
    # Generate the shapefile with the EOPatches
    geometry = [Polygon(bbox.get_polygon()) for bbox in bbox_list]
    idxs = [info['index'] for info in info_list]
    idxs_x = [info['index_x'] for info in info_list]
    idxs_y = [info['index_y'] for info in info_list]
    gdf = gpd.GeoDataFrame({'index': idxs, 'index_x': idxs_x, 'index_y': idxs_y}, 
                               crs=country.crs, 
                               geometry=geometry)

    gdf.to_file(shapefile_fullpath, driver='GPKG')
    
    return idxs, bbox_list


if __name__ == '__main__':
    patches = patchesGenerator(geospatialFolder, 'tile_Lith')