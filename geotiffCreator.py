import os, sys, shutil

# Sinergise libraries
from eolearn.core import EOPatch   

# geospatial libraries
from osgeo import gdal, ogr, osr
import numpy as np
# custom libraries
from general_functions import makepath
import datetime


# Global variables
mainDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData'
# mainDirectory = r'.\downloadData'
# outputDirectory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData'
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
            norm_image = np.round(image * 255)
            norm_image = norm_image.astype(np.uint8)
#             norm_image = cv2.normalize(image, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_32F) # MinMaxNormalization 0 to 255 
#             norm_image = norm_image.astype(np.uint8) # convert np.array to 8bit integer
            minValue = np.min(norm_image); maxValue = np.max(norm_image)
            if minValue == 0 and maxValue == 0: # delete the folder when the image has zero values
                if os.path.exists(tmpDir_fullpath) and os.path.isdir(tmpDir_fullpath):
                    shutil.rmtree(tmpDir_fullpath)
                continue
            else:                                                                
                outputName = f'{tmp_name}_B{i}.tiff'
                output_fullpath = os.path.join(tmpDir_fullpath, outputName)  
                DataSet = gdal.GetDriverByName(format).Create(output_fullpath, cols, rows, 1, gdal.GDT_Byte) # create 8bitfloat output image
                DataSet.SetGeoTransform((xmin, int(pixelRes), 0, ymax, 0, -int(pixelRes))) # transform the dataset 
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(UTM) 
                DataSet.SetProjection(srs.ExportToWkt())                      
                DataSet.GetRasterBand(1).WriteArray(norm_image) 
                DataSet = None
                print(output_fullpath)                
                

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
    

