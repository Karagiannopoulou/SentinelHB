# Default libs
import sys, os

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
    img = gdal.Open(filename_path)
    for band,b in zip(range(img.RasterCount),rgbBand_list): 
        band = band+1
        outputband = os.path.join(tile_folder,f'B{b}.tiff')
        gdal.Translate(outputband, img, format='GTiff', bandList=[band])
        print(outputband)

def create_single_band_image_drones(filename_path,tile_folder):
    img = gdal.Open(filename_path)
    for band in range(img.RasterCount):
        if band<3: 
            band = band+1
            outputband = os.path.join(tile_folder,f'B{band}.tiff')
            gdal.Translate(outputband, img, format='GTiff', bandList=[band])
            print(outputband)


def cognify(filename_path, outputpath, name, blocksize=2048, nodata=None):
    
    # blocksize: image size compression
    # nodata: verify if it is none or not    
    img = gdal.Open(filename_path)                   
    output_COG = os.path.join(outputpath,f'{name}_cog.tiff')
    gdaltranslate_options = f'-of COG -co COMPRESS=DEFLATE -co BLOCKSIZE={blocksize} -co RESAMPLING=AVERAGE -co OVERVIEWS=IGNORE_EXISTING -co PREDICTOR=YES'
    if nodata is not None: 
        gdaltranslate_options += ' -a_nodata ' + str(nodata)
    gdal.Translate(output_COG, img, options=gdaltranslate_options)
    
    print(output_COG)   
         

def unstack_image(input_path):
    
    # path: # as we build the file structure both in the root folder and the output folder, 
    # we isolate the folder path from the root and pasted to a variable that depicts the output folder 
    
    for folder in os.listdir(input_path):
        full_path = os.path.join(input_path, folder)
        print(full_path)
        for subfolder in os.listdir(full_path):
            if 'drones' in subfolder:
                subfolder_fullpath = os.path.join(full_path, subfolder)
                print(subfolder_fullpath)
                for ffile in os.listdir(subfolder_fullpath):
                    file_name = os.fsdecode(ffile) # decode file system
                    if file_name.endswith('.tif'):
                        filename_path = os.path.join(subfolder_fullpath, file_name)
                        name = os.path.splitext(os.path.basename(filename_path))[0]
                        img_date = name.split("_")[-1] 
                        print(img_date)
                        tileFolder_Name = os.path.join(subfolder_fullpath,img_date)
                        tile_folder = makepath(tileFolder_Name)
                        create_single_band_image_drones(filename_path,tile_folder)
            
            if 'Sentinel2' in subfolder:
                subfolder_fullpath = os.path.join(full_path, subfolder)         
                for ffile in os.listdir(subfolder_fullpath):
                    file_name = os.fsdecode(ffile) # decode file system
                    if file_name.endswith('.tif'):
                        filename_path = os.path.join(subfolder_fullpath, file_name) # initial file path of the image
                        name = os.path.splitext(os.path.basename(filename_path))[0]
                        img_date = name.split("_")[-1] # take the time of the image
                        rgbName = name.split("_")[1] # take the rgb of the image
                        rgbBand_list = split(rgbName) # split the part of the name showing the bands e.g. 567
                        if (len(rgbName)%2)==1 and rgbName in filename_path:
                            tileFolder_Name = os.path.join(subfolder_fullpath,img_date)
                            tile_folder = makepath(tileFolder_Name)
                            create_single_band_image_Sentinel(filename_path,rgbBand_list,tile_folder)
                         
                        elif (len(rgbName)%2)==0 and rgbName in filename_path:
                            create_single_band_image_Sentinel(filename_path,rgbBand_list,tile_folder)

def convert_images2COG(input_path): 
    # input path: define the main directory of the image
    # subfolder_prefix: the unique prefix that defines the subfolders containing the ImageSequence
    
    removeFiles_list = []
    
    for folder in os.listdir(input_path):
        folder_path = os.path.join(input_path, folder)
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path,subfolder)
            print(subfolder_path)
            for innerfolder in os.listdir(subfolder_path):
                innerfolderPath = os.path.join(subfolder_path, innerfolder)
                if os.path.isdir(innerfolderPath): 
                    for ffile in os.listdir(innerfolderPath):
                        filename_path = os.path.join(innerfolderPath, ffile)
                        name = os.path.splitext(os.path.basename(filename_path))[0]
                        removeFiles_list.append(filename_path)
                        if not filename_path.endswith('_cog.tiff'):
                            cognify(filename_path, innerfolderPath, name, blocksize=2048, nodata=None)  
                        else:
                            break

    for ffile in removeFiles_list:
        os.remove(ffile)                             
            


if __name__ == '__main__':
    unstack_image(main_Directory)
    convert_images2COG(main_Directory)
    