# Default libs
import sys, os

# Basics of GIS
from osgeo import gdal

mainDirectory = r'.\COG'

def congify(input_path, subfolder_prefix, blocksize=2048, nodata=None): 
    # input path: define the main directory of the image
    # subfolder_prefix: the unique prefix that defines the subfolders containing the images
    # blocksize: image size compression
    # nodata: verify if it is none or not 
    
    for root,dirs,_ in os.walk(input_path):
        for dir in dirs:
            subfolder = os.path.join(root,dir)
            if subfolder_prefix in subfolder:
                for file in os.listdir(subfolder):
                    filename_path = os.path.join(subfolder, file)
                    name = os.path.splitext(os.path.basename(filename_path))[0]
                    img = gdal.Open(filename_path)                   
                    output_COG = os.path.join(subfolder,f'{name}_cog.tiff')
                    print(output_COG)
                    gdaltranslate_options = f'-of COG -co COMPRESS=DEFLATE -co BLOCKSIZE={blocksize} -co RESAMPLING=AVERAGE -co OVERVIEWS=IGNORE_EXISTING -co PREDICTOR=YES'
                    if nodata is not None: 
                        gdaltranslate_options += ' -a_nodata ' + str(nodata)
                    gdal.Translate(output_COG, img, options=gdaltranslate_options)
                    
                                        
if __name__ == '__main__':
    congify(mainDirectory, '202')
    