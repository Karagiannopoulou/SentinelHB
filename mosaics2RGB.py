import os, sys

# libs related to time
import datetime
import time

# data manipulation
import numpy as np
import collections

# geospatial libs
import json 
import rasterio
from rasterio.merge import merge

# Custom scripts
from createMultibands import single2multi

start_time = time.time()

# Global variables
mainDirectory = r'.'
connectingFolder = r'D:\DIONE\WP3\SuperResolution'
# connectingFolder = r'\\192.168.111.2\Documents\Projects\EU_PROJECTS\DIONE\WP3\SuperResolution'

def makepath(path):
    try:
        os.mkdir(path)
    except OSError:
        print()
    return path  

def getDates(input_path, subfolder_prefix='out'):
    dateslist = []
    
    for dir in os.listdir(input_path):    
        if dir.startswith(subfolder_prefix):
            innerpath = os.path.join(input_path, dir)
            for innerFolder in os.listdir(innerpath):
                eopatchFolder = os.path.join(innerpath, innerFolder)
                for deepFolder in os.listdir(eopatchFolder):
                    if deepFolder.startswith('eo'):
                        sensingtime = deepFolder.split('_')[-1]
                        dateslist.append(sensingtime)
                    
                         
    return dateslist
    
def getSingleDates(input_path, list, subfolder_prefix='out'):    
    counter = collections.Counter(list);  # it's a list not a dictionary to take the keys with the
    # frequency of each single date
    dataDir10 = {}; dataDir20 = {} 
    
    for sensingTime in counter:    
        tmpList10 = []; tmpList20 = []         
        for dir in os.listdir(input_path):
            if dir.startswith(subfolder_prefix):           
                dirPath = os.path.join(input_path, dir)
                for folder in os.listdir(dirPath):
                    folderPath = os.path.join(dirPath, folder)
        
                    if 'eopatch_10' in folderPath:
                        for subfolder in os.listdir(folderPath):
                            if subfolder.endswith(sensingTime):
                                subfolder_path = os.path.join(folderPath, subfolder)                               
                                for filename in os.listdir(subfolder_path):
                                    filenamePath = os.path.join(subfolder_path, filename)                                    
                                    tmpList10.append(filenamePath)
                                    tmpDic_10 = {}
                                    tmpDic_10[sensingTime] = tmpList10
                                    dataDir10.update(tmpDic_10)
                                    
                    elif 'eopatch_20' in folderPath:
                        for subfolder in os.listdir(folderPath):
                            if subfolder.endswith(sensingTime):
                                subfolder_path = os.path.join(folderPath, subfolder)                               
                                for filename in os.listdir(subfolder_path):
                                    filenamePath = os.path.join(subfolder_path, filename)                                    
                                    tmpList20.append(filenamePath)
                                    tmpDic_20 = {};
                                    tmpDic_20[sensingTime] = tmpList20
                                    dataDir20.update(tmpDic_20) 

    return [dataDir10, dataDir20]

def getDictionary (dictionary_10, dictionary_20):
    # ini input and output variables     
    dict10 = dictionary_10; dict20 = dictionary_20 
    bandsList10 = ['B1', 'B2', 'B3', 'B4'] ; bandsList20 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
    tmpList10 = []; tmpList20 = [] 
    
    for values in dict10.values():
        tmp = {}
        for band in bandsList10:            
            filesList = []
            for ffile in values:           
                if band in ffile:
                    filesList.append(ffile)
            tmp[band] = filesList
        tmpList10.append(tmp)       
    dict10_keys = list(dict10.keys()) 
    mainDict10 = dict(zip(dict10_keys, tmpList10))
    
    with open("mainDict10.json", "w") as outfile:  
        json.dump(mainDict10, outfile) 
    
    
    for values in dict20.values():
        tmp = {}
        for band in bandsList20:            
            filesList = []
            for ffile in values:           
                if band in ffile:
                    filesList.append(ffile)
            tmp[band] = filesList
        tmpList20.append(tmp)       
    dict20_keys = list(dict20.keys()) 
    mainDict20 = dict(zip(dict20_keys, tmpList20))
    
    with open("mainDict20.json", "w") as outfile:  
        json.dump(mainDict20, outfile) 
    
    

def createMosaics (json_10, json_20, root=mainDirectory, outputroot=connectingFolder):
    
    Lith_foldername10 = 'Lith_output10'; Lith_foldername20 = 'Lith_output20' 
    Cy_foldername10 = 'CY_output10'; Cy_foldername20 = 'CY_output20' 
    
    dict10 = f'{root}\{json_10}'; dict20 = f'{root}\{json_20}'
    J10 = open(dict10); J20 = open(dict20)
    dictJSON_10 = json.load(J10); dictJSON_20 = json.load(J20)  

    
    for (key,value) in dictJSON_10.items():
        for idx, subvalue in enumerate(value.values()):
            band = idx+1 # to create the band name  
            mosaicList10 = []
            for ffile in subvalue:
                src = rasterio.open(ffile)
                mosaicList10.append(src)                    

            mosaic, out_trans = merge(mosaicList10)
            out_meta = src.meta.copy()
            
            if out_meta['crs'] == 'EPSG:32634':
                out_meta.update({"driver": "GTiff",
                                  "height": mosaic.shape[1],
                                  "width": mosaic.shape[2],
                                  "transform": out_trans,
                                  "crs": "+proj=utm +zone=34 +ellps=GRS80 +units=m +no_defs "
                                  }
                                 )
                
                tmpname = f'mosaic_{Lith_foldername10}'
                tmppath = os.path.join(outputroot, tmpname)
                tmppathFinal = makepath(tmppath)
                if band ==1:
                    mosaicfolder = os.path.join(tmppath,key) 
                    if not os.path.exists(mosaicfolder):
                        os.makedirs(mosaicfolder)
                        print(mosaicfolder)
                mosaicName = f'S2_mosaic_{key}_B{band}.tiff'
                mosaicName_fullpath = os.path.join(mosaicfolder, mosaicName)
                print(f'mosaic name Lithuania: {mosaicName_fullpath}')
                
                with rasterio.open(mosaicName_fullpath, "w", **out_meta) as dest:
                    dest.write(mosaic)
    
            elif out_meta['crs'] == 'EPSG:32636':  
                out_meta.update({"driver": "GTiff",
                                  "height": mosaic.shape[1],
                                  "width": mosaic.shape[2],
                                  "transform": out_trans,
                                  "crs": "+proj=utm +zone=36 +ellps=GRS80 +units=m +no_defs "
                                  }
                                 )   
                
                tmpname = f'mosaic_{Cy_foldername10}'
                tmppath = os.path.join(outputroot, tmpname)
                tmppathFinal = makepath(tmppath)  
                if band ==1:
                    mosaicfolder = os.path.join(tmppath,key) 
                    if not os.path.exists(mosaicfolder):
                        os.makedirs(mosaicfolder)
                        print(mosaicfolder) 
                mosaicName = f'S2_mosaic_{key}_B{band}.tiff'
                mosaicName_fullpath = os.path.join(mosaicfolder, mosaicName)
                print(f'mosaic name Cyprus: {mosaicName_fullpath}')
                
                with rasterio.open(mosaicName_fullpath, "w", **out_meta) as dest:
                    dest.write(mosaic)
    
    for (key,value) in dictJSON_20.items():
        for idx, subvalue in enumerate(value.values()):
            band = idx+1 # to create the band name  
            mosaicList20 = []
            for ffile in subvalue:
                src = rasterio.open(ffile)
                mosaicList20.append(src)                    

            mosaic, out_trans = merge(mosaicList20)
            out_meta = src.meta.copy()
            
            if out_meta['crs'] == 'EPSG:32634':
                out_meta.update({"driver": "GTiff",
                                  "height": mosaic.shape[1],
                                  "width": mosaic.shape[2],
                                  "transform": out_trans,
                                  "crs": "+proj=utm +zone=34 +ellps=GRS80 +units=m +no_defs "
                                  }
                                 )
                
                tmpname = f'mosaic_{Lith_foldername20}'
                tmppath = os.path.join(outputroot, tmpname)
                tmppathFinal = makepath(tmppath)
                if band ==1:
                    mosaicfolder = os.path.join(tmppath,key) 
                    if not os.path.exists(mosaicfolder):
                        os.makedirs(mosaicfolder)
                        print(mosaicfolder)        
                mosaicName = f'S2_mosaic_{key}_B{band}.tiff'
                mosaicName_fullpath = os.path.join(mosaicfolder, mosaicName)
                print(f'mosaic name Lithuania: {mosaicName_fullpath}')
                
                with rasterio.open(mosaicName_fullpath, "w", **out_meta) as dest:
                    dest.write(mosaic)
            
            elif out_meta['crs'] == 'EPSG:32636':  
                out_meta.update({"driver": "GTiff",
                                  "height": mosaic.shape[1],
                                  "width": mosaic.shape[2],
                                  "transform": out_trans,
                                  "crs": "+proj=utm +zone=36 +ellps=GRS80 +units=m +no_defs "
                                  }
                                 )   
                tmpname = f'mosaic_{Cy_foldername20}'
                tmppath = os.path.join(outputroot, tmpname)
                tmppathFinal = makepath(tmppath)
                if band ==1:
                    mosaicfolder = os.path.join(tmppath,key) 
                    if not os.path.exists(mosaicfolder):
                        os.makedirs(mosaicfolder)
                        print(mosaicfolder)        
                mosaicName = f'S2_mosaic_{key}_B{band}.tiff'
                mosaicName_fullpath = os.path.join(mosaicfolder, mosaicName)
                print(f'mosaic name Cyprus: {mosaicName_fullpath}')
                
                with rasterio.open(mosaicName_fullpath, "w", **out_meta) as dest:
                    dest.write(mosaic)                   



if __name__ == '__main__':
    dateslists = getDates(mainDirectory)    
    datesDictionaries = getSingleDates(mainDirectory, dateslists)
    getDictionary(datesDictionaries[0], datesDictionaries[1])
    createMosaics('mainDict10.json', 'mainDict20.json')
    RGBmosaics = single2multi(connectingFolder)
    
      
elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))