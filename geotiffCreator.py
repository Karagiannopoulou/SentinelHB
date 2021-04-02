import os,sys

# Sinergise libraries
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

# geospatial libraries
from osgeo import gdal, ogr, osr
import numpy as np
# custom libraries
from general_functions import makepath

# Global variables
mainDirectory = r'.'
outputDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData'

def geotiff_Generator(subdirPath, dateslist, outputsubPath, UTM, format = 'GTiff'):
    name = os.path.basename(os.path.normpath(subdirPath))
    pixelRes = name.split('_')[1] # change the resolution based on the name of the eopatch folder
    eopatch = EOPatch.load(subdirPath, lazy_loading=False)
#                     cols = eopatch.meta_info['size_x']
#                     rows = eopatch.meta_info['size_y']
    xmin,ymin,xmax,ymax = eopatch.bbox
    timestamp = eopatch.timestamp
    for time,arr in zip(list(timestamp),eopatch.data['L2A_data']):
        datetime_str = time.strftime('%Y%m%dT%H%M%S')
        dateslist.append(datetime_str)
        tmp_name = f'{name}_{datetime_str}'
        tmp_fullpath = os.path.join(outputsubPath, tmp_name)
        tmpDir_fullpath = makepath(tmp_fullpath)
                                       
        cols,rows,bands= np.shape(arr)                                                                  
        data = np.moveaxis(arr, -1, 0) # reshape the dimensions of the array to have the bands first                        
        for i, image in enumerate(data, 1):
            image[image==0] = np.nan                                                              
            outputName = f'{tmp_name}_B{i}.tiff'
            output_fullpath = os.path.join(tmpDir_fullpath,outputName)
            print(output_fullpath)                              
            DataSet = gdal.GetDriverByName(format).Create(output_fullpath, cols, rows, 1, gdal.GDT_Float32) # create the output image
            DataSet.SetGeoTransform((xmin, int(pixelRes), 0, ymax, 0, -int(pixelRes))) # transform the dataset 
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(UTM) 
            DataSet.SetProjection(srs.ExportToWkt())                      
            DataSet.GetRasterBand(1).WriteArray(image) 
            DataSet = None


def export2TIFF(mainroot, outputDirectory, subfolder_prefix = 'out'):
    # input path: the main directory where the eopatches are stored
    # output directory: where the geotiffs will be exported 
    # subfolder prefix: a prefix such as the word 'out' that indicates the specific folder where the eopatches are stored
    # format: by default it was set to export the images in geotiff
    
    dateslist = []
    for dir in os.listdir(mainroot):
        if dir.startswith(subfolder_prefix):
            dirPath = os.path.join(mainroot, dir)
            outputPath = os.path.join(outputDirectory, dir)
            outputdirPath = makepath(outputPath)                            
            for subdir in os.listdir(dirPath):
                subdirPath = os.path.join(dirPath, subdir) 
                outputsubPath = os.path.join(outputdirPath, subdir)
                outputsubdirPath = makepath(outputsubPath)         
                
                if not "_CY" in subdirPath:
                    geotiff_Generator(subdirPath, dateslist, outputsubPath, 32634)   
                                              
                if "_CY" in subdirPath:
                    geotiff_Generator(subdirPath, dateslist, outputsubPath, 32636)

if __name__ == '__main__':
    export2TIFF(mainDirectory, outputDirectory)
    

