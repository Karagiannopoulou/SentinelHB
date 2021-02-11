# Default libs
import sys
import os

# Basics of GIS
from osgeo import gdal
mainDirectory = r'.\COG'

def unstack_image(input_path):
    for root, dirs, files in os.walk(input_path, topdown=True):  
        for dir in dirs:
            full_path = os.path.join(input_path, dir)
            for file in os.listdir(full_path):
                filename = os.fsdecode(file)
                if filename.endswith(".tif"):                          
                    filename_path = os.path.join(full_path, filename)
                    name = os.path.splitext(os.path.basename(filename_path))[0]

                    tile_folder = os.path.join(full_path,name) # create folders from the name of the images
                                            
                    if not(os.path.exists(tile_folder) and os.path.isdir(tile_folder)):
                        os.makedirs(tile_folder)

                        img = gdal.Open(filename_path)
                        for band in range(img.RasterCount): #Save bands as individual files
                            band = band+1
                            outputband = os.path.join(tile_folder,f'B{band}.tiff')
                            print(outputband)
                            gdal.Translate(outputband, img, format='GTiff', bandList=[band])
                            
                                
                                           
                        


if __name__ == '__main__':
    unstack_image(mainDirectory)
    