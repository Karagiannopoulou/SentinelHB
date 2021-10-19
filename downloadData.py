#!/usr/bin/env python
# Default libs
import os, sys

# Data visualisation/Datetime
import json 
import datetime

# Sentinel Hub libs
from eolearn.core import SaveTask, FeatureType, LinearWorkflow, OverwritePermission, EOExecutor
from eolearn.io import SentinelHubInputTask
from sentinelhub import SHConfig, DataCollection 

# import custom scripts
from secrets import INSTANCE_ID, CLIENT_ID, CLIENT_SECRET
from general_functions import makepath, cleanFolder
from getEOPatches import createGeoJson, patchesGenerator, splitpatches_Lithuania, splitpatches_Cyprus

# Define local paths 
root = r'.'
ini_folder = r'D:\DIONE\WP3\SuperResolution\downloadData_2021'
logsFolder = r'.\logsFolder'
# Load wkt with the AOI
geospatialFolder = r'.\bbox'

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


def downloadEO_Lithuania(input_folder, input_task10, input_task20, updatedPatches_Lth, time_interval):
        path10_Lth = os.path.join(input_folder, 'output10'); path20_Lth = os.path.join(input_folder, 'output20')
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


def downloadEO_Cyprus(input_folder, input_task10, input_task20, updatedPatches_Cy, time_interval):
        
        path10_Cy = os.path.join(input_folder, 'output10_CY'); path20_Cy = os.path.join(input_folder, 'output20_CY')
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



def dynamic_startDate(root):
    
    dict10 ={}; dict20={}; list_with_dates_10 = []; list_with_dates_20 = [] 
    
    for ffile in os.listdir(root):
        if 'mainDict10' in ffile:
            jsonsPath10 = os.path.join(root, ffile)
            json10 = open(jsonsPath10)
            dict10=json.load(json10)          
                        
        elif 'mainDict20' in ffile:
            jsonsPath20 = os.path.join(root, ffile)
            json20 = open(jsonsPath20)
            dict20=json.load(json20)
    
    for (key10,key20) in zip(dict10.keys(), dict20.keys()):
        date_dts10 = datetime.datetime.strptime(key10, '%Y%m%dT%H%M%S')
        date_dts20 = datetime.datetime.strptime(key20, '%Y%m%dT%H%M%S')
        list_with_dates_10.append(date_dts10); list_with_dates_20.append(date_dts20)
    
    # calculate the latest datetime of a list with images dates
    youngest10 = max(list_with_dates_10); youngest20 = max(list_with_dates_20)
    
    # pic the latest date. Compare the youngest date that is calculated for the json 10, and 20 and take the most current. 
    # We expect to be the same always but you never know.
    if youngest10>youngest20:
        youngest10_Str = youngest10.strftime('%Y-%m-%d')
        time_start=youngest10_Str
    elif youngest20>youngest10:
        youngest20_Str = youngest20.strftime('%Y-%m-%d')
        time_start=youngest20_Str
    else:
        youngest10_Str = youngest10.strftime('%Y-%m-%d')
        time_start=youngest10_Str
    
    return time_start                                                                                                                   


def starting_time(root):
    
    if any(File.startswith("mainDict") for File in os.listdir(root)): # check if a json exists. if no it means that the process is initiated for the first time and the data will be the taken from the else.
        latest_Date = dynamic_startDate(root) # get the latest date 
        latest_Date_datetime = datetime.datetime.strptime(latest_Date, '%Y-%m-%d')
        starting_Date_datetime = latest_Date_datetime + datetime.timedelta(days=1) # get one day after and define it as the start date... 
        starting_Date = starting_Date_datetime.strftime('%Y-%m-%d')
    else:
        starting_Date = '2021-03-01'
    
    return starting_Date
    
def downloadEO(resolution, start_date, maxcc=0.1):
    
    # Initialize variables 
    country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus = createGeoJson(geospatialFolder, 'LithAOI.json', 'CyAOI.json')    
    bbox_list_Lithuania, info_list_Lithuania, bbox_list_Cyprus, info_list_Cyprus = patchesGenerator(country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus) 
    updatedPatches_Lth = splitpatches_Lithuania(geospatialFolder, country_Lithuania, bbox_list_Lithuania, info_list_Lithuania)
    updatedPatches_Cy = splitpatches_Cyprus(geospatialFolder, country_Cyprus, bbox_list_Cyprus, info_list_Cyprus)
    
    # remove older log folders
    cleanFolder(root, subfolder_prefix='logs')
    
    # Define the start date and end date   
    start_datetime = start_date
    now = datetime.datetime.now() # activate this in automated process
    end_datetime = now.strftime('%Y-%m-%d') # activate this in automated process
    # time_interval = (start_datetime, end_datetime) # activate this in automated process
    time_interval = (start_datetime, '2021-09-30') # activate this in case of manual process
    
    # Define the parameters for the service request
    input_task10 = SentinelHubInputTask(
        data_collection=DataCollection.SENTINEL2_L2A,
        bands=['B02','B03','B04','B08'], #10m
        bands_feature=(FeatureType.DATA, 'L2A_data'),
        resolution=resolution[0],
        maxcc=maxcc,
        time_difference=datetime.timedelta(hours=6),
        config=config,
        max_threads=5
    )
    
    input_task20 = SentinelHubInputTask(
        data_collection=DataCollection.SENTINEL2_L2A,
        bands=['B05','B06','B07','B8A','B11','B12'], #20m
        bands_feature=(FeatureType.DATA, 'L2A_data'),
        resolution=resolution[1],
        maxcc=maxcc,
        time_difference=datetime.timedelta(hours=6),
        config=config,
        max_threads=5
    )
    
    downloadEO_Lithuania(ini_folder, input_task10, input_task20, updatedPatches_Lth, time_interval)
    
    downloadEO_Cyprus(ini_folder, input_task10, input_task20, updatedPatches_Cy, time_interval)
     


if __name__ == '__main__':
    start_datetime = starting_time()
    downloadEO(resolution, start_datetime)















