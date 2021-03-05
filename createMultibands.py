import os, sys

# libs related to time
import datetime
import time

from osgeo import gdal

start_time = time.time()

connectingFolder = r'D:\DIONE\WP3\SuperResolution'

def single2multi(outputroot):
    
    for dir in os.listdir(outputroot):
        innerpath = os.path.join(outputroot, dir)
        if innerpath.endswith('output10'):
            for folder in os.listdir(innerpath): 
                folderPath = os.path.join(innerpath, folder)
                VRTname = os.path.basename(folderPath)
                bandList10 = []
                for i, ffile in enumerate(os.listdir(folderPath)):
                    band = i+1
                    if band==1 and str(band) in ffile: 
                        bandList10.append(os.path.join(folderPath,ffile))
                    if band==2 and str(band) in ffile:
                        bandList10.append(os.path.join(folderPath,ffile))
                    if band==3 and str(band) in ffile:
                        bandList10.append(os.path.join(folderPath,ffile))  
                        
                tifs = bandList10
                print(tifs)
                mosaicfolder = f'{folderPath}\multiband'
                if not os.path.exists(mosaicfolder): 
                    os.makedirs(mosaicfolder)
                outVRT = f'{mosaicfolder}\VRT_{VRTname}.vrt'
                outTIFF = f'{mosaicfolder}\S2_234_mosaic_{VRTname}.tiff'
                outds = gdal.BuildVRT(outVRT, tifs, separate=True)
                outds = gdal.Translate(outTIFF, outds)
                os.remove(outVRT)
                print(outTIFF)
                
        elif innerpath.endswith('output20'):
            for folder in os.listdir(innerpath): 
                folderPath = os.path.join(innerpath, folder)
                VRTname = os.path.basename(folderPath)
                bandList20_567 = []; bandList20_8a1112 = []
                for i, ffile in enumerate(os.listdir(folderPath)):
                    band = i+1
                    if band==1 and str(band) in ffile: 
                        bandList20_567.append(os.path.join(folderPath,ffile))
                    if band==2 and str(band) in ffile:
                        bandList20_567.append(os.path.join(folderPath,ffile))
                    if band==3 and str(band) in ffile:
                        bandList20_567.append(os.path.join(folderPath,ffile))
                    if band==4 and str(band) in ffile:
                        bandList20_8a1112.append(os.path.join(folderPath,ffile)) 
                    if band==5 and str(band) in ffile:
                        bandList20_8a1112.append(os.path.join(folderPath,ffile))
                    if band==6 and str(band) in ffile:
                        bandList20_8a1112.append(os.path.join(folderPath,ffile))
                
                # RGB for the 567 spectral bands        
                tifs_567 = bandList20_567
                print(tifs_567)
                mosaicfolder = f'{folderPath}\multiband'
                if not os.path.exists(mosaicfolder): 
                    os.makedirs(mosaicfolder)
                    
                outVRT_567 = f'{mosaicfolder}\VRT_567_{VRTname}.vrt'
                outTIFF_567 = f'{mosaicfolder}\S2_567_mosaic_{VRTname}.tiff'
                outds_567 = gdal.BuildVRT(outVRT_567, tifs_567, separate=True)
                outds_567 = gdal.Translate(outTIFF_567, outds_567)
                os.remove(outVRT_567) 
                print(outTIFF_567)  
                
                # RGB for the 8a1112 spectral bands                        
                tifs_8a1112 = bandList20_8a1112
                print(tifs_8a1112)
                mosaicfolder = f'{folderPath}\multiband'
                if not os.path.exists(mosaicfolder): 
                    os.makedirs(mosaicfolder)
                outVRT_8a1112 = f'{mosaicfolder}\VRT_8a1112_{VRTname}.vrt'
                outTIFF_8a1112 = f'{mosaicfolder}\S2_8a1112_mosaic_{VRTname}.tiff'
                outds_8a1112 = gdal.BuildVRT(outVRT_8a1112, tifs_8a1112, separate=True)
                outds_8a1112 = gdal.Translate(outTIFF_8a1112, outds_8a1112)
                os.remove(outVRT_8a1112)      
                print(outTIFF_8a1112)             


if __name__ == '__main__':
    single2multi(connectingFolder)
    
    
    
      
elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


