#!/usr/bin/env python
# Default libs
import sys
import os

# Data manipulation/visualisation libs
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd

# Basics of GIS
import geopandas as gpd
from shapely.geometry import Polygon

# The core of this example
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

# Misc
import pickle
import datetime
import itertools
import enum

def dataDir(path):
    '''
    Create directory if not exists
    '''
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)

# Define the path or Create in terms of absence
path  = r'.\atest10'
path2  = r'.\atest20'

# Credentials 
INSTANCE_ID   = ''
CLIENT_ID     = ''
CLIENT_SECRET = ''

# Try to connect
config = SHConfig()
try:
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID: 
        config.instance_id = INSTANCE_ID
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
except:
    if config.sh_client_id == '' & config.sh_client_secret == '' & config.instance_id == '': 
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")

# Load boundaries of the AOI in GeoJson format
country = gpd.read_file(r'bbox\my.json') # Lithuania tile

# Transform GeoJSON projection and find the dimensions 
country_crs = CRS.UTM_34N
country     = country.to_crs(crs={'init': CRS.ogc_string(country_crs)})

# Get the country's shape in polygon format
country_shape = country.geometry.values[-1]

# Create the splitter to obtain a list of bboxes
bbox_splitter = UtmZoneSplitter([country_shape], country.crs, 24000) # 35 patches per S2 image tile 
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



shapefile_name = 'C:\Users\karagiannopoulou\eclipse-workspace\dioneSH2\bbox\grid_LithuaniaT24k.gpkg'
gdf.to_file(shapefile_name, driver='GPKG')

# Download the data 
# Initialize variables
# time_interval = ('2020-01-01','2020-01-15')
maxcc = 0.9 # 10% maximum cloud coverage on images
resolution = [10,20] 

s2_l2a_mundi = DataCollection.define_from(DataCollection.SENTINEL2_L2A,'SENTINEL2_L2A_MUNDI',service_url='https://shservices.mundiwebservices.com')

input_task10 = SentinelHubInputTask(
    data_collection=s2_l2a_mundi,
    bands=['B02','B03','B04','B08'], #10m
    bands_feature=(FeatureType.DATA, 'L2A_data'),
    resolution=resolution[0],
    maxcc=maxcc,
    time_difference=datetime.timedelta(hours=2),
    config=config,
    max_threads=5
)

input_task20 = SentinelHubInputTask(
    data_collection=s2_l2a_mundi,
    bands=['B05','B06','B07','B8A','B11','B12'], #20m
    bands_feature=(FeatureType.DATA, 'L2A_data'),
    resolution=resolution[1],
    maxcc=maxcc,
    time_difference=datetime.timedelta(hours=2),
    config=config,
    max_threads=5
)

load = LoadTask(path)

# TASK FOR SAVING TO OUTPUT (if needed)
save1 = SaveTask(path, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)

workflow = LinearWorkflow(
    input_task10,
    save1
)

# Execute the workflow
time_interval = ('2021-01-01', datetime.datetime.today())

execution_args = []

for idx, bbox in enumerate(bbox_list[idxs]):
    print("Processing: %s"%(idx))
    tmp = {
        input_task10:{'bbox': bbox, 'time_interval': time_interval},
        save1: {'eopatch_folder': f'eopatch_{idx}'},
    }
    
    execution_args.append(tmp)
    executor = EOExecutor(workflow, [tmp], save_logs=True)
    executor.run(workers=4, multiprocess=False)
    executor.make_report()
    tiff_name = f'eopatch_{idx}.tiff'
    ind_path = f'{path}\eopatch_{idx}'
    eopatch = EOPatch.load(ind_path, lazy_loading=False)
    bands_feature_exp=(FeatureType.DATA, 'L2A_data')
    eopath2tiff = ExportToTiff(bands_feature_exp, folder=path2)
    eopath2tiff.execute(eopatch, filename=tiff_name)

sys.exit()






