import os, sys, shutil
# Sinergise libraries
from eolearn.core import EOPatch   
# geospatial libraries
from osgeo import gdal, osr
import numpy as np
from skimage.util import img_as_ubyte
from skimage import exposure
# custom libraries
from general_functions import makepath

# Global variables
mainDirectory = outputDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData_2021'
# outputDirectory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData_2021'

def geotiff_Generator(subdirPath, outputsubPath, UTM, format = 'GTiff'):
    # subdirPath: it is the eopatches folder path e.g. .\downloadData\output10\eopatch_10_0
    name = os.path.basename(os.path.normpath(subdirPath)) # getting the eopatches name from folder (e.g eopatch_10_0)
    pixelRes = name.split('_')[1] # getting the spatial resolution from the folder name
    eopatch = EOPatch.load(subdirPath, lazy_loading=False) # read the data included in the EOpatch cube
    xmin,ymin,xmax,ymax = eopatch.bbox
    timestamp = eopatch.timestamp
    
    for time,arr in zip(list(timestamp),eopatch.data['L2A_data']):
        datetime_str = time.strftime('%Y%m%dT%H%M%S')
#         dateslist.append(datetime_str)   
        tmp_name = f'{name}_{datetime_str}' # create the eopatch folder e.g.eopatch_10_0_20210305T094513
        tmp_fullpath = os.path.join(outputsubPath, tmp_name)
        tmpDir_fullpath = makepath(tmp_fullpath)                             
        cols,rows,bands= np.shape(arr)                                                                  
        data = np.moveaxis(arr, -1, 0) # reshape the dimensions of the array to have the bands first                        
        for i, image in enumerate(data, 1):
            min_image_value = np.min(image); max_image_value = np.max(image)
            # print("min {}".format(min_image_value))
            # print("max {}".format(max_image_value))
            # sys.exit()
            if min_image_value == 0 and max_image_value == 0: # delete the folder when the image has zero values
                try:
                    print('folder: {} deleted'.format(tmp_fullpath))
                    shutil.rmtree(tmpDir_fullpath)
                except FileNotFoundError:
                    continue
            elif min_image_value != max_image_value and os.path.exists(tmpDir_fullpath)==False:
                print('continue')
                continue
            else:
                outputName = f'{tmp_name}_B{i}.tiff'
                output_fullpath = os.path.join(tmpDir_fullpath, outputName)
                DataSet = gdal.GetDriverByName(format).Create(output_fullpath, cols, rows, 1, gdal.GDT_UInt16) # create 16bit unsigned integer output image
                DataSet.SetGeoTransform((xmin, int(pixelRes), 0, ymax, 0, -int(pixelRes))) # transform the dataset
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(UTM)
                DataSet.SetProjection(srs.ExportToWkt())
                DataSet.GetRasterBand(1).WriteArray(image)
                DataSet = None
                print(output_fullpath)
                

def export2TIFF(input_folder, outputDirectory, subfolder_prefix = 'out'):
    # input path: the main directory where the eopatches are stored
    # output directory: where the geotiffs will be exported 
    # subfolder prefix: a prefix such as the word 'out' that indicates the specific folder where the eopatches are stored
    # format: by default it was set to export the images in geotiff
    
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
                    geotiff_Generator(subdirPath, outputsubdirPath, 32634)       
                if "_CY" in subdirPath:
                    geotiff_Generator(subdirPath, outputsubdirPath, 32636)

if __name__ == '__main__':
    export2TIFF(mainDirectory, outputDirectory)