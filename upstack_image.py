# Default libs
import sys, os

# Basics of GIS
from osgeo import gdal

# Global vars
mainDirectory = r'.\COG'

def split(word):
    n=2 
    if (len(word)%2)==1: # odd length if the bands are 3 (5,6,7)
        return [char for char in word]
    elif (len(word)%2)==0:  # even length if the bands are 6 (8a,11,12)
        return [word[index : index + n] for index in range(0, len(word), n)]
            

def unstack_image(input_path, subfolder_prefix):
    for _, dirs,_ in os.walk(input_path):  
        for folder in dirs:
            full_path = os.path.join(input_path, folder)
            if subfolder_prefix in full_path:
                for file in os.listdir(full_path):
                    file_name = os.fsdecode(file) # decode filesystem
                    if file_name.endswith(".tif"):                          
                        filename_path = os.path.join(full_path, file_name)
                        name = os.path.splitext(os.path.basename(filename_path))[0] 
                        img_date = name.split("_")[-1] # take the time of the image
                        rgbName = name.split("_")[1] # take the rgb of the image
                        rgbBand_list = split(rgbName)
    
                        if (len(rgbName)%2)==1 and rgbName in filename_path:
                            tile_folder = os.path.join(full_path,img_date) # create folders from the name of the images                                
                            if not os.path.exists(tile_folder):
                                os.makedirs(tile_folder)
                                img = gdal.Open(filename_path)
                                for band,b in zip(range(img.RasterCount),rgbBand_list): 
                                    band = band+1
                                    outputband = os.path.join(tile_folder,f'B{b}.tiff')
                                    gdal.Translate(outputband, img, format='GTiff', bandList=[band])
                                    print(outputband)
                        
                        if (len(rgbName)%2)==0 and rgbName in filename_path:
                            if os.path.exists(tile_folder):
                                
                                img = gdal.Open(filename_path)
                                for band,b in zip(range(img.RasterCount),rgbBand_list): 
                                    band = band+1                                     
                                    outputband = os.path.join(tile_folder,f'B{b}.tiff')
                                    gdal.Translate(outputband, img, format='GTiff', bandList=[band])
                                    print(outputband)

if __name__ == '__main__':
    unstack_image(mainDirectory, 'tile')
    