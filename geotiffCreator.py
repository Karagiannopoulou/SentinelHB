import os,sys, shutil

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
mainDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData'
outputDirectory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData'

def geotiff_Generator(subdirPath, dateslist, outputsubPath, UTM, format = 'GTiff'):
    # subdirPath: it is the eopatches folder path e.g. .\downloadData\output10\eopatch_10_0
    
    name = os.path.basename(os.path.normpath(subdirPath)) # getting the eopatches (e.g eopatch_10_0)
    pixelRes = name.split('_')[1] # getting the spatial resolution from the folder name
    eopatch = EOPatch.load(subdirPath, lazy_loading=False)
    xmin,ymin,xmax,ymax = eopatch.bbox
    timestamp = eopatch.timestamp
    for time,arr in zip(list(timestamp),eopatch.data['L2A_data']):
        datetime_str = time.strftime('%Y%m%dT%H%M%S')
        dateslist.append(datetime_str)
        tmp_name = f'{name}_{datetime_str}' # create the eopatch folder e.g.eopatch_10_0_20210305T094513
        tmp_fullpath = os.path.join(outputsubPath, tmp_name)
        tmpDir_fullpath = makepath(tmp_fullpath)                             
        cols,rows,bands= np.shape(arr)                                                                  
        data = np.moveaxis(arr, -1, 0) # reshape the dimensions of the array to have the bands first                        
        for i, image in enumerate(data, 1):
            minValue = float("{:.3f}".format(np.min(image)))
            maxValue = float("{:.3f}".format(np.max(image)))
            if minValue == 0.0 and maxValue == 0.0: # delete the folder when the image has zero values
                if os.path.exists(tmpDir_fullpath) and os.path.isdir(tmpDir_fullpath):
                    shutil.rmtree(tmpDir_fullpath)
                continue
            else:                                                                
                outputName = f'{tmp_name}_B{i}.tiff'
                output_fullpath = os.path.join(tmpDir_fullpath,outputName)            
                DataSet = gdal.GetDriverByName(format).Create(output_fullpath, cols, rows, 1, gdal.GDT_Byte) # create 8bit output image
                DataSet.SetGeoTransform((xmin, int(pixelRes), 0, ymax, 0, -int(pixelRes))) # transform the dataset 
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(UTM) 
                DataSet.SetProjection(srs.ExportToWkt())                      
                DataSet.GetRasterBand(1).WriteArray(image) 
                DataSet = None


def export2TIFF(input_folder, outputDirectory, subfolder_prefix = 'out'):
    # input path: the main directory where the eopatches are stored
    # output directory: where the geotiffs will be exported 
    # subfolder prefix: a prefix such as the word 'out' that indicates the specific folder where the eopatches are stored
    # format: by default it was set to export the images in geotiff
    
    dateslist = []
    for dir in os.listdir(input_folder):
        if dir.startswith(subfolder_prefix):
            dirPath = os.path.join(input_folder, dir)
            outputPath = os.path.join(outputDirectory, dir)
            outputdirPath = makepath(outputPath)                            
            for subdir in os.listdir(dirPath):
                subdirPath = os.path.join(dirPath, subdir) 
                outputsubPath = os.path.join(outputdirPath, subdir)
                outputsubdirPath = makepath(outputsubPath)         
                
                if not "_CY" in subdirPath:
                    geotiff_Generator(subdirPath, dateslist, outputsubdirPath, 32634)   
                                              
                if "_CY" in subdirPath:
                    geotiff_Generator(subdirPath, dateslist, outputsubdirPath, 32636)

if __name__ == '__main__':
    export2TIFF(mainDirectory, outputDirectory)
    

