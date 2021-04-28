# sys libraries
import os,sys

# time libraries
import time, schedule  

# Custom libs
from downloadData import starting_time, downloadEO
from geotiffCreator import export2TIFF
from mosaics import getDictionary, createMosaics
from general_functions import cleanFolder
from createMultibands import single2multi

# start counting processing time
start_time = time.time()

# define the resolution of the spectral bands
resolution = [10,20]
root = r'.'
mainDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData'
outputDirectory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData'


def downloader():
#     Download Sentinel-2 data
#     print('Initiating the process .........')
#     start_datetime = starting_time(root)
#     print(start_datetime)
#     downloadEO(resolution, start_datetime)
    
    # convert to geotiff
    print('Starting to export the geotiffs .........')
    export2TIFF(mainDirectory, outputDirectory)
    print('exporting end!')
    
    # create mosaics and multiband stack mosaics
    print('Starting creating mosaics.........')
    getDictionary(root, outputDirectory)
    createMosaics(outputDirectory)
    cleanFolder(outputDirectory, subfolder_prefix='out') # clean the folders containing the data from which the mosaics were created
    single2multi(outputDirectory)
    print('multistack mosaics are ready')


def main():
    downloader()
    schedule.every(5).days.do(downloader) # revisit time of Sentinel-2
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    

if __name__ == '__main__':
    main()
    
# end counting processing time
elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))    

