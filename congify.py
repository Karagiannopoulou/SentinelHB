# Default libs
import sys, os, shutil

# Basics of GIS
from osgeo import gdal
from general_functions import makepath
 
# Global vars
main_Directory = r'D:\DIONE\WP3\SuperResolution\uploadData'

def split(word):
    n=2 
    if (len(word)%2)==1: # odd length if the bands are 3 (5,6,7)
        return [char for char in word]
    elif (len(word)%2)==0:  # even length if the bands are 6 (8a,11,12)
        return [word[index : index + n] for index in range(0, len(word), n)]


def create_single_band_image_Sentinel(filename_path,rgbBand_list,tile_folder):  
    # create two list, band list including the band names, and the output_image_fullpath including the file path. Then we will iterate these list to congify the images on them
    
    band_list = []; output_image_fullpath = [] 
    img = gdal.Open(filename_path)
    
    for band,b in zip(range(img.RasterCount),rgbBand_list): 
        band = band+1
        band_name = "B{}".format(b) # we create this and provided it as an output in the return to be an input in the congify function
        band_name_tiff = "B{}.tiff".format(b) # output band name including the tiff prefix, generating the geotiff single band file 
        outputband = os.path.join(tile_folder,band_name_tiff) # output full path file name, included in the return to be also an input in the congify function
    #         print("output band: {}".format(outputband))
        gdal.Translate(outputband, img, format='GTiff', bandList=[band])
        band_list.append(band_name)
        output_image_fullpath.append(outputband)
        
    return band_list, output_image_fullpath

def create_single_band_image_drones(filename_path,tile_folder):
    # create two list, band list including the band names, and the output_image_fullpath including the file path. Then we will iterate these list to congify the images on them
    
    band_list = []; output_image_fullpath = []
    img = gdal.Open(filename_path)
    
    for band in range(img.RasterCount):
        if band<3: 
            band = band+1
            band_name = "B{}".format(band) # we create this and provided it as an output in the return to be an input in the congify function
            band_name_tiff = "B{}.tiff".format(band) # output band name including the tiff prefix, generating the geotiff single band file 
            outputband = os.path.join(tile_folder,band_name_tiff) # output full path file name, included in the return to be also an input in the congify function
            gdal.Translate(outputband, img, format='GTiff', bandList=[band])
            band_list.append(band_name)
            output_image_fullpath.append(outputband)
            
    return band_list, output_image_fullpath

def cognify_image(filename_path, outputpath, band_name, blocksize=2048, nodata=None):
    # blocksize: image size compression
    # nodata: verify if it is none or not
    
    img = gdal.Open(filename_path)                   
    output_COG = os.path.join(outputpath,f'{band_name}_cog.tiff')
    gdaltranslate_options = f'-of COG -co COMPRESS=DEFLATE -co BLOCKSIZE={blocksize} -co RESAMPLING=AVERAGE -co OVERVIEWS=IGNORE_EXISTING -co PREDICTOR=YES'
    if nodata is not None: 
        gdaltranslate_options += ' -a_nodata ' + str(nodata)
    gdal.Translate(output_COG, img, options=gdaltranslate_options)
    
    return output_COG  
    
    