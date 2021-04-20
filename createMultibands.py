import os, sys
import json
from osgeo import gdal

root = r'.'
connectingFolder = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData'


def getting_newdates(root):
    dict10 ={}; dict20={}; list_with_dates_10 = []; list_with_dates_20 = [] 
    
    for ffile in os.listdir(root):
        if 'mainDict10' in ffile:
            jsonsPath10 = os.path.join(root, ffile)
            json10 = open(jsonsPath10)
            dict10=json.load(json10)          
                        
        elif 'mainDict20' in ffile:
            jsonsPath20 = os.path.join(root, ffile)
            json20 = open(jsonsPath20)
            dict20=json.load(json20)
    
    for (key10,key20) in zip(dict10.keys(), dict20.keys()):
        list_with_dates_10.append(key10); list_with_dates_20.append(key20)

    return list_with_dates_10, list_with_dates_20



def multiband_stack_geotiff(bandList, folderPath, rgb_name, VRTname):
    tifs = bandList
    mosaicfolder = os.path.join(folderPath,'multiband')
    if not os.path.exists(mosaicfolder): 
        os.makedirs(mosaicfolder)
    outVRTName = f'VRT_{rgb_name}_{VRTname}.vrt'
    outVRT = os.path.join(mosaicfolder, outVRTName)
    outTiffName = f'S2_{rgb_name}_mosaic_{VRTname}.tiff'
    outTIFF = os.path.join(mosaicfolder, outTiffName)
    outds = gdal.BuildVRT(outVRT, tifs, separate=True)
    outds = gdal.Translate(outTIFF, outds)
    os.remove(outVRT)


def single2multi(outputroot):
    list_newDates10 , list_newDates20 = getting_newdates(root)
    
    for dir in os.listdir(outputroot):
        innerpath = os.path.join(outputroot, dir)
        if innerpath.endswith('output10'):
            for folder in os.listdir(innerpath):
                if folder in list_newDates10: 
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
                    
                    multiband_stack_geotiff(bandList10, folderPath, VRTname, '234')
                    
        elif innerpath.endswith('output20'):
            for folder in os.listdir(innerpath): 
                if folder in list_newDates20: 
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
                multiband_stack_geotiff(bandList20_567, folderPath, VRTname, '567')
                 
                # RGB for the 8a1112 spectral bands
                multiband_stack_geotiff(bandList20_8a1112, folderPath, VRTname, '8a1112')
                            


if __name__ == '__main__':
    single2multi(connectingFolder)
    



