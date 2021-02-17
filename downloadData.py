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

# The core of this example
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 




# Define global variables 
# Path for nparrays
path10  = r'.\output10'
path20  = r'.\output20'

# Credentials and authorisation     
INSTANCE_ID   = ''
CLIENT_ID     = ''
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

# Load wkt with the AOI
geospatialFolder = r'bbox'

# Variables for the downloadEO function
resolution = [10,20]

def dataDir(outputpath_10, outputpath_20):
    '''
    Create directory if not exists
    '''
    try:
        os.mkdir(outputpath_10)
        os.mkdir(outputpath_10)
    except OSError:
        print ("Creation of the directory %s failed" % outputpath_10)
        print ("Creation of the directory %s failed" % outputpath_20)
    else:
        print ("Successfully created the directory %s" % outputpath_10)
        print ("Successfully created the directory %s" % outputpath_20)
    return[outputpath_10, outputpath_20]  

def createGeoJson(geospatialFolder, filename):
    
    AOI = os.path.join(geospatialFolder, filename)
    print(AOI)
   
    # Load boundaries of the AOI in GeoJson format
    country = gpd.read_file(AOI) # Lithuania tile

    # Transform GeoJSON projection and find the dimensions 
    country_crs = CRS.UTM_34N
    country = country.to_crs(crs={'init': CRS.ogc_string(country_crs)})
    
    # Get the country's shape in polygon format
    country_shape = country.geometry.values[-1]
    return [country, country_shape]

def patchesGenerator(country, country_shape, outputname, patches = 24000):  
    
    shapefile_name = f'{outputname}.gpkg'
    shapefile_fullpath = os.path.join(geospatialFolder,shapefile_name)  
    
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
    
    return [idxs, bbox_list]

def downloadEO(maxcc, resolution, path10, path20, idxs, bbox_list):
    
    time_interval = ('2021-01-01', datetime.datetime.today())
    
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
    
    save10 = SaveTask(path10, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
    save20 = SaveTask(path20, overwrite_permission=OverwritePermission.OVERWRITE_PATCH)
    
    workflow10 = LinearWorkflow(
        input_task10,
        save10
    )
    workflow20 = LinearWorkflow(
        input_task20,
        save20
    ) 
    execution_args10 = []; execution_args20 = []
    
    for idx, bbox in enumerate(bbox_list[idxs]):
        print("Processing: %s"%(idx))
        tmp10 = {
            input_task10:{'bbox': bbox, 'time_interval': time_interval},
            save10: {'eopatch_folder': f'eopatch_10_{idx}'},
        }
        
        tmp20 = {
            input_task20:{'bbox': bbox, 'time_interval': time_interval},
            save20: {'eopatch_folder': f'eopatch_20_{idx}'},
        }
        
        execution_args10.append(tmp10)
        executor10 = EOExecutor(workflow10, [tmp10], save_logs=True, logs_folder=path10)
        executor10.run(workers=4, multiprocess=False)
        executor10.make_report()
        
        execution_args20.append(tmp20)
        executor20 = EOExecutor(workflow20, [tmp20], save_logs=True, logs_folder=path20)
        executor20.run(workers=4, multiprocess=False)
        executor20.make_report()
    


def main():
    paths = dataDir(path10,path20)
    shape = createGeoJson(geospatialFolder, 'my.json')
    patches = patchesGenerator(shape[0],shape[1], 'tile_Lth')
    bbox_list=patches[1]; idxs_G = patches[0]
    eopatches = downloadEO(0.1, resolution, paths[0], paths[1], idxs_G, bbox_list)
    print(eopatches)
    


if __name__ == '__main__':
    main()

