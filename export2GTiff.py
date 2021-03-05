import os,sys

# Sinergise libraries
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

# geospatial libraries
from osgeo import gdal, ogr, osr

import numpy as np
import datetime
import time

start_time = time.time()

# Global variables
mainDirectory = r'.'
resolution = [10,20]


def Export2Tiff(input_path, subfolder_prefix, format = 'GTiff'):
    # input path: the main directory where the eopatches are stored
    # subfolder prefix: a prefix such as the word 'out' that indicates the specific folder where the eopatches are stored
    # format: by default it was set to export the images in geotiff
    dateslist = []
        
    for root, dirs, _ in os.walk(input_path):
        for subfolder in dirs:
            if subfolder_prefix in subfolder:
                innerpath = os.path.join(root, subfolder)
                for innerfolder in os.listdir(innerpath):
                    inner_subfolder = os.path.join(innerpath, innerfolder)
                    name = os.path.basename(os.path.normpath(inner_subfolder))
                    pixelRes = name.split('_')[1] # change the resolution based on the name of the eopatch folder
                    eopatch = EOPatch.load(inner_subfolder, lazy_loading=False)
#                     cols = eopatch.meta_info['size_x']
#                     rows = eopatch.meta_info['size_y']
                    xmin,ymin,xmax,ymax = eopatch.bbox
                    timestamp = eopatch.timestamp
                    for time,arr in zip(list(timestamp),eopatch.data['L2A_data']):
                        datetime_str = time.strftime('%Y%m%dT%H%M%S')
                        dateslist.append(datetime_str)

                        tmp_name = f'{name}_{datetime_str}'
                        tmp_fullpath = os.path.join(inner_subfolder, tmp_name)
                        if not os.path.exists(tmp_fullpath):
                            os.makedirs(tmp_fullpath)                                                                
                            cols,rows,bands= np.shape(arr)                                                                  
                            data = np.moveaxis(arr, -1, 0) # reshape the dimensions of the array to have the bands first                        
                             
                            for i, image in enumerate(data, 1):
                                outputName = f'{tmp_name}_B{i}.tiff'
                                output_fullpath = os.path.join(tmp_fullpath,outputName)
                                print(output_fullpath)                              
                                 
                                DataSet = gdal.GetDriverByName(format).Create(output_fullpath, cols, rows, 1, gdal.GDT_Float32) # create the output image
                                DataSet.SetGeoTransform((xmin, int(pixelRes), 0, ymax, 0, -int(pixelRes))) # transform the dataset 
                                srs = osr.SpatialReference()
                                srs.ImportFromEPSG(32634) 
                                DataSet.SetProjection(srs.ExportToWkt())                      
                                DataSet.GetRasterBand(1).WriteArray(image) 
                                DataSet = None

if __name__ == '__main__':
    Export2Tiff(mainDirectory, 'out')
    
    
    
elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
