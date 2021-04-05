# sys libraries
import os,sys

# time libraries
import time, schedule

# Sentinel Hub libs
from eolearn.core import *
from eolearn.io import *
from sentinelhub import * 

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
mainDirectory = r'.'
outputDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData'


def downloader():
    # Download Sentinel-2 data
    start_datetime = starting_time()
    downloadEO(resolution, start_datetime)
    
    # convert to geotiff
    print('Starting to export the geotiffs .........')
    export2TIFF(mainDirectory, outputDirectory)
    print('exporting end!')
    
    # create mosaics and multiband stack mosaics
    print('Starting creating mosaics.........')
    getDictionary(mainDirectory)
    createMosaics(mainDirectory, outputDirectory)
    cleanFolder(outputDirectory, subfolder_prefix='out') # clean the folders containing the data from which the mosaics were created
    single2multi(outputDirectory)
    print('multistack mosaics are ready')


def main():
    downloader()
    schedule.every(2).days.at("07:00").do(downloader())
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    

if __name__ == '__main__':
    main()
    
    
# end counting processing time
elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
