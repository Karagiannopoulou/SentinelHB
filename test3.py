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
from eolearn.core import EOTask, EOPatch, LinearWorkflow, FeatureType, \
    LoadTask, OverwritePermission, LoadFromDisk, SaveToDisk, SaveTask, EOExecutor
from eolearn.io import SentinelHubInputTask, ExportToTiff
from sentinelhub import BBoxSplitter, BBox, CRS, UtmZoneSplitter, SHConfig, DataCollection 

# Misc
import pickle
import datetime
import itertools
import enum

# Define the path or Create in terms of absence
path = r'./test10'
path2 = r'./test20'

# Credentials 
# INSTANCE_ID = ''
INSTANCE_ID = ''
CLIENT_ID = ''
CLIENT_SECRET = ''

config = SHConfig()

try:
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID: 
        config.instance_id = INSTANCE_ID
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
except:
    if config.sh_client_id == '' & config.sh_client_secret == '' & config.instance_id == '': 
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")


def dataDir():
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)



# Load boundaries of the AOI in GeoJson format
country = gpd.read_file(r'bbox/my.json') # Lithuania tile

# Transform GeoJSON projection and find the dimensions 
country_crs = CRS.UTM_34N
country = country.to_crs(crs={'init': CRS.ogc_string(country_crs)})
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



shapefile_name = './bbox/grid_LithuaniaT24k.gpkg'
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

# save2 = SaveTask(path2, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)

# export_tiff = ExportToTiff(FeatureType.DATA, 'BANDS')
#export_tiff = ExportToTiff((FeatureType.MASK_TIMELESS, 'LBL_GBM'))

# export_tiff = ExportToTiff(feature=(FeatureType.DATA, 'BANDS'))


# Define the workflow
workflow = LinearWorkflow(
    input_task10,
    #input_task20,
    #save1,
#     load,
    #export_tiff,
    save1
)


# workflow2 = LinearWorkflow(
#     load,
#     export_tiff,
#     save2
#     
#     )


# Execute the workflow
time_interval = ('2021-01-01', datetime.datetime.today())

execution_args = []

ini_path = r'C:\Users\karagiannopoulou\eclipse-workspace\dioneSH2\test10'

for idx, bbox in enumerate(bbox_list[idxs]):
    tmp = {
        input_task10:{'bbox': bbox, 'time_interval': time_interval},
        #input_task20:{'bbox': bbox, 'time_interval': time_interval},
        #save1: {'eopatch_folder': f'eopatch_{idx}'},
#             load: {'eopatch_folder': f'eopatch_{idx}'},
#             export_tiff:{'filename':str((os.path.join(path,"test.tiff")))},
        save1: {'eopatch_folder': f'eopatch_{idx}'},
    }
    

#     tmp2 = {
#         load: {'eopatch_folder': f'eopatch_{idx}'}, 
#         export_tiff:{'filename':str((os.path.join(path,f"{tiff_name}")))},
#         save2: {'eopatch_folder': f'eopatch_{idx}'}
#         
#         }
#     
    execution_args.append(tmp)
#     execution_args.append(tmp2)
    executor = EOExecutor(workflow, [tmp], save_logs=True)
    executor.run(workers=5, multiprocess=False)
    executor.make_report()
     
    
    tiff_name = f'eopatch_{idx}.tiff'
    path = f'{ini_path}/eopatch_{idx}'
    path2 = os.path.join(path2, f'eopatch_{idx}')
    eopatch = EOPatch.load(path, lazy_loading=True)
    eopath2tiff = ExportToTiff((FeatureType.DATA, 'L2A_data'), folder=path2)
    print(eopath2tiff)
    x = eopath2tiff.execute(eopatch, filename=tiff_name)
    print(x)
    
    
    
    
    
        
    
    
#     execution_args2.append(tmp2)
#     executor2=EOExecutor(workflow2, [tmp2], save_logs=True)
#     executor2.run(workers=5, multiprocess=False)
#     executor2.make_report()


        
    sys.exit()






