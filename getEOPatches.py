#!/usr/bin/env python
# Default libs
import sys, os
# Data manupulation/time
import numpy as np
import datetime, time
# Geospatial libs
import geopandas as gpd
from shapely.geometry import Polygon
# Sentinel Hub libs
from sentinelhub import * 

# Load wkt with the AOI
geospatialFolder = r'.\bbox'

# Variables for the downloadEO function
def createGeoJson(input_folder, filename_Lithuania, filename_Cyprus):
    # AOI: define the json file with the AOI's boundaries
    # country: read it as geopandas
    # country's_crs: transform projection to UTM zone
    # country's shape: get the shape in polygon format    
    
    AOI_Lithuania = os.path.join(input_folder, filename_Lithuania)    
    country_Lithuania = gpd.read_file(AOI_Lithuania)
    country_crs_Lithuania = CRS.UTM_34N    
    country_Lithuania = country_Lithuania.to_crs(crs={'init': CRS.ogc_string(country_crs_Lithuania)})
    country_shape_Lithuania = country_Lithuania.geometry.values[-1]
    
    AOI_Cyprus = os.path.join(input_folder, filename_Cyprus)    
    country_Cyprus = gpd.read_file(AOI_Cyprus)
    country_crs_Cyprus = CRS.UTM_36N   
    country_Cyprus = country_Cyprus.to_crs(crs={'init': CRS.ogc_string(country_crs_Cyprus)})
    country_shape_Cyprus = country_Cyprus.geometry.values[-1]
    
    return country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus

def patchesGenerator(country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus, patches = 24000):   
     
    # bbox splitter: Create the splitter to obtain a list of bboxes and create the EOpatches
    # bbox list: list with the eopatches 
    # idxs: list with the indexes of the eopatches     
    # ini variables
    
    # Lithuania case 
    bbox_splitter_Lithuania = UtmZoneSplitter([country_shape_Lithuania], country_Lithuania.crs, patches) # 35 patches per S2 image tile
    bbox_list_Lithuania = np.array(bbox_splitter_Lithuania.get_bbox_list())
    info_list_Lithuania = np.array(bbox_splitter_Lithuania.get_info_list())    
    idxs = [info['index'] for info in info_list_Lithuania]  
    
    # Cyprus case
    bbox_splitter_Cyprus = UtmZoneSplitter([country_shape_Cyprus], country_Cyprus.crs, patches) # 35 patches per S2 image tile
    bbox_list_Cyprus = np.array(bbox_splitter_Cyprus.get_bbox_list())
    info_list_Cyprus = np.array(bbox_splitter_Cyprus.get_info_list())    
    idxs = [info['index'] for info in info_list_Cyprus] 
    
    return bbox_list_Lithuania, info_list_Lithuania, bbox_list_Cyprus, info_list_Cyprus

  
def splitpatches_Lithuania(input_folder, country_Lithuania, bbox_list_Lithuania, info_list_Lithuania, outputname='final_tiles_Lith'):  
    
    shapefile_name_Lith = f'{outputname}.gpkg'
    shapefile_fullpath_Lith = os.path.join(input_folder,shapefile_name_Lith)
    updated_bbox_list_Lithuania = np.array([]); updated_info_list_Lithuania = np.array([])
    unwantedTiles_Lithuania = [0,1,2,3,4,5,6,12,18,24,30]
    
    # update the lists with the eopatches 
    for ((i,tile),infoList) in zip(enumerate(bbox_list_Lithuania),info_list_Lithuania):       
        if not i in unwantedTiles_Lithuania:
            updated_bbox_list_Lithuania = np.append(updated_bbox_list_Lithuania, tile)
            updated_info_list_Lithuania = np.append(updated_info_list_Lithuania, infoList)   
    
    # create a dict with static the information of the coordinate system and a dict with none the indices that will being changed
    final_info_dict_Lithuania = {'crs': 'UTM_34N', 'utm_zone': '34', 'utm_row': '', 'direction': 'N'}
    changedDict = {}.fromkeys(['index', 'index_x', 'index_y'], '')
    final_info_dict_Lithuania.update(changedDict)   
    
    final_info_list_Lithuania = []
      
    for arr in updated_info_list_Lithuania:
        index = arr['index']; index_x = arr['index_x']; index_y = arr['index_y']        
        if index_x ==1 and index_y <6:
            index_up = index-7; index_x_up = index_x-1; index_y_up = index_y-1            
            final_info_dict_Lithuania['index'] = index_up
            final_info_dict_Lithuania['index_x'] = index_x_up
            final_info_dict_Lithuania['index_y'] = index_y_up
            final_info_list_Lithuania.append(final_info_dict_Lithuania.copy())    
        
        if index_x ==2 and index_y <6:
            index_up = index-8; index_x_up = index_x-1; index_y_up = index_y-1
            final_info_dict_Lithuania['index'] = index_up
            final_info_dict_Lithuania['index_x'] = index_x_up
            final_info_dict_Lithuania['index_y'] = index_y_up
            final_info_list_Lithuania.append(final_info_dict_Lithuania.copy())
         
        if index_x ==3 and index_y <6:
            index_up = index-9; index_x_up = index_x-1; index_y_up = index_y-1
            final_info_dict_Lithuania['index'] = index_up
            final_info_dict_Lithuania['index_x'] = index_x_up
            final_info_dict_Lithuania['index_y'] = index_y_up
            final_info_list_Lithuania.append(final_info_dict_Lithuania.copy())
             
        if index_x ==4 and index_y <6:
            index_up = index-10; index_x_up = index_x-1; index_y_up = index_y-1
            final_info_dict_Lithuania['index'] = index_up
            final_info_dict_Lithuania['index_x'] = index_x_up
            final_info_dict_Lithuania['index_y'] = index_y_up
            final_info_list_Lithuania.append(final_info_dict_Lithuania.copy())
         
        if index_x ==5 and index_y <6:
            index_up = index-11; index_x_up = index_x-1; index_y_up = index_y-1
            final_info_dict_Lithuania['index'] = index_up
            final_info_dict_Lithuania['index_x'] = index_x_up
            final_info_dict_Lithuania['index_y'] = index_y_up
            final_info_list_Lithuania.append(final_info_dict_Lithuania.copy())
    
    final_array_list_Lithuania = np.array(final_info_list_Lithuania)     
    geometry_Lth = [Polygon(bbox.get_polygon()) for bbox in updated_bbox_list_Lithuania]
    idxs_Lithuania = [info['index'] for info in final_array_list_Lithuania]
    idxs_x_Lithuania = [info['index_x'] for info in final_array_list_Lithuania]
    idxs_y_Lithuania = [info['index_y'] for info in final_array_list_Lithuania]
    gdf = gpd.GeoDataFrame({'index': idxs_Lithuania, 'index_x': idxs_x_Lithuania, 'index_y': idxs_y_Lithuania}, crs=country_Lithuania.crs, geometry=geometry_Lth)
    gdf.to_file(shapefile_fullpath_Lith, driver='GPKG') # remember to put an if statement 

    return [idxs_Lithuania, updated_bbox_list_Lithuania]

def splitpatches_Cyprus(input_folder, country_Cyprus, bbox_list_Cyprus, info_list_Cyprus, outputname='final_tiles_Cy'): 
    
    shapefile_name_Cy = f'{outputname}.gpkg'
    shapefile_fullpath_Cy = os.path.join(input_folder, shapefile_name_Cy)  
    
    updated_bbox_list_Cyprus = np.array([]); updated_info_list_Cyprus = np.array([]) 
    wantedTiles_Cyprus = [2, 3, 4, 8, 9, 10, 11, 15, 16, 17, 21, 22, 28]    
    # update the lists with the eopatches 
    for ((i,tile),infoList) in zip(enumerate(bbox_list_Cyprus),info_list_Cyprus):       
        if i in wantedTiles_Cyprus:
            updated_bbox_list_Cyprus = np.append(updated_bbox_list_Cyprus, tile)
            updated_info_list_Cyprus = np.append(updated_info_list_Cyprus, infoList)   
    
    # create a dict with static the information of the coordinate system and none the indices that will being changed
    final_info_dict_Cyprus = {'crs': 'UTM_36N', 'utm_zone': '36', 'utm_row': '', 'direction': 'N'}
    changedDict = {}.fromkeys(['index', 'index_x', 'index_y'], '')
    final_info_dict_Cyprus.update(changedDict)
   
    final_info_list_Cyprus = []
      
    for arr in updated_info_list_Cyprus:
        index = arr['index']; index_x = arr['index_x']; index_y = arr['index_y']        
        if index_x ==0 and index_y <5:
            index_up = index-2; index_x_up = index_x; index_y_up = index_y-2            
            final_info_dict_Cyprus['index'] = index_up
            final_info_dict_Cyprus['index_x'] = index_x_up
            final_info_dict_Cyprus['index_y'] = index_y_up
            final_info_list_Cyprus.append(final_info_dict_Cyprus.copy())
        
        if index_x==1 and index_y<6:
            index_up = index-5; index_x_up = index_x; index_y_up = index_y-2 
            final_info_dict_Cyprus['index'] = index_up
            final_info_dict_Cyprus['index_x'] = index_x_up
            final_info_dict_Cyprus['index_y'] = index_y_up
            final_info_list_Cyprus.append(final_info_dict_Cyprus.copy())
        
        if index_x==2 and index_y<6:
            index_up = index-8; index_x_up = index_x; index_y_up = index_y-3 
            final_info_dict_Cyprus['index'] = index_up
            final_info_dict_Cyprus['index_x'] = index_x_up
            final_info_dict_Cyprus['index_y'] = index_y_up
            final_info_list_Cyprus.append(final_info_dict_Cyprus.copy()) 
        
        if index_x==3 and index_y<5:
            index_up = index-11; index_x_up = index_x; index_y_up = index_y-3 
            final_info_dict_Cyprus['index'] = index_up
            final_info_dict_Cyprus['index_x'] = index_x_up
            final_info_dict_Cyprus['index_y'] = index_y_up
            final_info_list_Cyprus.append(final_info_dict_Cyprus.copy())   
        
        if index_x==4 and index_y==4:
            index_up = index-16; index_x_up = index_x; index_y_up = index_y-4 
            final_info_dict_Cyprus['index'] = index_up
            final_info_dict_Cyprus['index_x'] = index_x_up
            final_info_dict_Cyprus['index_y'] = index_y_up
            final_info_list_Cyprus.append(final_info_dict_Cyprus.copy())
        
    
    final_array_list_Cyprus = np.array(final_info_list_Cyprus)    
    geometry_Lth = [Polygon(bbox.get_polygon()) for bbox in updated_bbox_list_Cyprus]
    idxs_Cyprus = [info['index'] for info in final_array_list_Cyprus]
    idxs_x_Cyprus = [info['index_x'] for info in final_array_list_Cyprus]
    idxs_y_Cyprus = [info['index_y'] for info in final_array_list_Cyprus]
    gdf = gpd.GeoDataFrame({'index': idxs_Cyprus, 'index_x': idxs_x_Cyprus, 'index_y': idxs_y_Cyprus}, crs=country_Cyprus.crs, geometry=geometry_Lth)
    gdf.to_file(shapefile_fullpath_Cy, driver='GPKG') # remember to put an if statement 
     
    return [idxs_Cyprus, updated_bbox_list_Cyprus]

if __name__ == '__main__':
    country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus = createGeoJson(geospatialFolder, 'LithAOI.json', 'CyAOI.json')
    bbox_list_Lithuania, info_list_Lithuania, bbox_list_Cyprus, info_list_Cyprus = patchesGenerator(country_Lithuania, country_shape_Lithuania, country_Cyprus, country_shape_Cyprus)
    splitpatches_Lithuania(geospatialFolder, country_Lithuania, bbox_list_Lithuania, info_list_Lithuania)
    splitpatches_Cyprus(geospatialFolder, country_Cyprus, bbox_list_Cyprus, info_list_Cyprus)
    
    
    