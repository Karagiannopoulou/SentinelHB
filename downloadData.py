#!/usr/bin/env python
# Default libs
import sys
import os

# Data visualisation/Datetime
import numpy as np
import datetime
import time

# Basics of GIS
import geopandas as gpd
from shapely.geometry import Polygon

# Sentinel Hub libs
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

# import custom scripts
from general_functions import makepath
from getEOPatches import createGeoJson, patchesGenerator, splitpatches_Lithuania, splitpatches_Cyprus

start_time = time.time()

# Define local paths 
mainroot = r'.'
logsFolder = r'.\logsFolder'
# Load wkt with the AOI
geospatialFolder = r'bbox'

# Credentials and authorisation     
INSTANCE_ID   = 'f12d5fd9-5d83-474a-a4a7-9b90adc6e27f'
CLIENT_ID     = '629e3c27-b93e-4990-83d5-106707ffff1b'
CLIENT_SECRET = 's}lwWt}EUC6Irw0D7H[Cf5Q[G[]QT51aAg6|8W#%'

config = SHConfig()
try:
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID: 
        config.instance_id = INSTANCE_ID
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
except:
    if config.sh_client_id == '' & config.sh_client_secret == '' & config.instance_id == '': 
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")

# Variables for the downloadEO function
resolution = [10,20]


def downloadEO_Lithuania(mainroot, input_task10, input_task20, updatedPatches_Lth, time_interval):
        path10_Lth = os.path.join(mainroot, 'output10'); path20_Lth = os.path.join(mainroot, 'output20')
        path10_Lithuania = makepath(path10_Lth); path20_Lithuania = makepath(path20_Lth)
        
        idxs = updatedPatches_Lth[0]; bbox_list = updatedPatches_Lth[1] 
        
        save10 = SaveTask(path10_Lithuania, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
        save20 = SaveTask(path20_Lithuania, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
        
        workflow10= LinearWorkflow(
            input_task10, 
            save10
        )
        
        workflow20 = LinearWorkflow(
            input_task20,
            save20
        )
        
        execution_args10 = []; execution_args20 = []
    
    
        for idx, bbox in enumerate(bbox_list[idxs]):
            print(f'Processing Lithuania:{idx}')
            
            tmp10 = {
                input_task10:{'bbox': bbox, 'time_interval': time_interval},
                save10: {'eopatch_folder': f'eopatch_10_{idx}'}
                }
            
            tmp20 = {
                input_task20:{'bbox': bbox, 'time_interval': time_interval},
                save20: {'eopatch_folder': f'eopatch_20_{idx}'}
                }
        
            execution_args10.append(tmp10)
            executor10 = EOExecutor(workflow10, [tmp10], save_logs=True, logs_folder=logsFolder)
            executor10.run(workers=4, multiprocess=False)
            executor10.make_report()
            
            execution_args20.append(tmp20)
            executor20 = EOExecutor(workflow20, [tmp20], save_logs=True, logs_folder=logsFolder)
            executor20.run(workers=4, multiprocess=False)
            executor20.make_report()


def downloadEO_Cyprus(mainroot, input_task10, input_task20, updatedPatches_Cy, time_interval):
        
        path10_Cy = os.path.join(mainroot, 'output10_CY'); path20_Cy = os.path.join(mainroot, 'output20_CY')
        path10_Cyprus = makepath(path10_Cy); path20_Cyprus = makepath(path20_Cy)
        
        cidxs = updatedPatches_Cy[0]; cbbox_list = updatedPatches_Cy[1]

        save10 = SaveTask(path10_Cyprus, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
        save20 = SaveTask(path20_Cyprus, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
        
        workflow10= LinearWorkflow(
            input_task10, 
            save10
        )
        
        workflow20 = LinearWorkflow(
            input_task20,
            save20
        )
        
        execution_args10 = []; execution_args20 = []
    
    
        for idx, bbox in enumerate(cbbox_list[cidxs]):
            print(f'Processing Cyprus:{idx}')
            
            tmp10 = {
                input_task10:{'bbox': bbox, 'time_interval': time_interval},
                save10: {'eopatch_folder': f'eopatch_10_{idx}'}
                }
            
            tmp20 = {
                input_task20:{'bbox': bbox, 'time_interval': time_interval},
                save20: {'eopatch_folder': f'eopatch_20_{idx}'}
                }
        
            execution_args10.append(tmp10)
            executor10 = EOExecutor(workflow10, [tmp10], save_logs=True, logs_folder=logsFolder)
            executor10.run(workers=4, multiprocess=False)
            executor10.make_report()
            
            execution_args20.append(tmp20)
            executor20 = EOExecutor(workflow20, [tmp20], save_logs=True, logs_folder=logsFolder)
            executor20.run(workers=4, multiprocess=False)
            executor20.make_report()


def downloadEO(resolution, maxcc=0.1):
    
    shape = createGeoJson(geospatialFolder, 'LithAOI.json', 'CyAOI.json')    
    patchesList = patchesGenerator(shape[0],shape[1],shape[2],shape[3])
    updatedPatches_Lth = splitpatches_Lithuania(shape[0], patchesList[0], patchesList[1])
    updatedPatches_Cy = splitpatches_Cyprus(shape[2], patchesList[2], patchesList[3])
    
    time_interval = ('2021-01-01', '2021-02-28')
    
    input_task10 = SentinelHubInputTask(
        data_collection=DataCollection.SENTINEL2_L2A,
        bands=['B02','B03','B04','B08'], #10m
        bands_feature=(FeatureType.DATA, 'L2A_data'),
        resolution=resolution[0],
        maxcc=maxcc,
        time_difference=datetime.timedelta(hours=2),
        config=config,
        max_threads=5
    )
    
    input_task20 = SentinelHubInputTask(
        data_collection=DataCollection.SENTINEL2_L2A,
        bands=['B05','B06','B07','B8A','B11','B12'], #20m
        bands_feature=(FeatureType.DATA, 'L2A_data'),
        resolution=resolution[1],
        maxcc=maxcc,
        time_difference=datetime.timedelta(hours=2),
        config=config,
        max_threads=5
    )
    
    downloadEO_Lithuania(mainroot, input_task10, input_task20, updatedPatches_Lth, time_interval)
    
    downloadEO_Cyprus(mainroot, input_task10, input_task20, updatedPatches_Cy, time_interval)
    
    
    


if __name__ == '__main__':
    downloadEO(resolution)


elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))













