# sys libraries
import os,sys

# time libraries
import time, schedule
from datetime import datetime  

# Custom libs
from downloadData import starting_time, downloadEO
from geotiffCreator import export2TIFF
from mosaics import createMosaics
from general_functions import cleanFolder
from createMultibands import single2multi

# define the resolution of the spectral bands
resolution = [10,20]
root = r'.'
mainDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData_2021'
outputDirectory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData_2021'
# outputDirectory = r'D:\DIONE\WP3\SuperResolution\downloadData_2021'

def downloader():
    Download Sentinel-2 data
    print('Initiating the process .........')
    start_datetime = starting_time(root)
    print(start_datetime)
    downloadEO(resolution, start_datetime)

    # convert to geotiff
    print('Starting to export the geotiffs .........')
    export2TIFF(mainDirectory, outputDirectory)
    print('exporting end!')
     
    # create mosaics and multiband stack mosaics
    print('Starting creating mosaics.........')    
    createMosaics(root, outputDirectory)
    cleanFolder(outputDirectory, subfolder_prefix='out') # clean the folders containing the data from which the mosaics were created
    single2multi(outputDirectory)
    print('multistack mosaics are ready')
    print(datetime.now())


def main():
    downloader()
    schedule.every(15).days.do(downloader) 
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    

if __name__ == '__main__':
    main()
    
 

