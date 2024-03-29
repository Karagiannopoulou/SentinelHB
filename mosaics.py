import os, sys
# libs related to time
from datetime import datetime
# data manipulation
import collections, json
# geospatial libs
import rasterio
from rasterio.merge import merge
# Custom scripts
from general_functions import makepath

# Global variables
root = r'.'
connectingFolder = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\downloadData_2021'

def getDates(input_folder, subfolder_prefix='out'):
    dateslist = []
    
    for dir in os.listdir(input_folder):    
        if dir.startswith(subfolder_prefix):
            innerpath = os.path.join(input_folder, dir)
            for innerFolder in os.listdir(innerpath):
                eopatchFolder = os.path.join(innerpath, innerFolder)
                for deepFolder in os.listdir(eopatchFolder):
                    if deepFolder.startswith('eo'):
                        sensingtime = deepFolder.split('_')[-1]
                        dateslist.append(sensingtime)
                    
                         
    return dateslist
    
def get_first_dictionaries(input_folder, subfolder_prefix='out'): 
    
    dateslists = getDates(input_folder) 
    counter = collections.Counter(dateslists)  # it's a list not a dictionary to take the keys with the single dates
    single_dates = sorted(counter) # sort the dates because they are sorted based on maximum counts and not by the closest date
    
    dataDict10 = {}; dataDict20 = {} 
    
    for sensingTime in single_dates:   
        tmpList10 = []; tmpList20 = []         
        for dir in os.listdir(input_folder):
            if dir.startswith(subfolder_prefix):           
                dirPath = os.path.join(input_folder, dir)
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
                                    dataDict10.update(tmpDic_10)
                                    
                    elif 'eopatch_20' in folderPath:
                        for subfolder in os.listdir(folderPath):
                            if subfolder.endswith(sensingTime):
                                subfolder_path = os.path.join(folderPath, subfolder)                               
                                for filename in os.listdir(subfolder_path):
                                    filenamePath = os.path.join(subfolder_path, filename)                                    
                                    tmpList20.append(filenamePath)
                                    tmpDic_20 = {};
                                    tmpDic_20[sensingTime] = tmpList20
                                    dataDict20.update(tmpDic_20) 

    return dataDict10, dataDict20


def get_jsons_for_mosaic(root, input_folder):    
         
    dict10, dict20 = get_first_dictionaries(input_folder)   

    bandsList10 = ['B1', 'B2', 'B3', 'B4'] ; bandsList20 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
    tmpList10 = []; tmpList20 = [] 
    
    # remove the older dictionaries in order to write the new ones    
    for ffile in os.listdir(root):
        if ffile.startswith('mainDict'):
            os.remove(ffile)
            print("json files deleted")
    
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
    
    # Add in the json filename the datetime of its creation. 
    now = datetime.now()
    dt_string = now.strftime('%Y%m%d')
    mainDict10json_Name = f'mainDict10_{dt_string}.json'
    
    with open(mainDict10json_Name, "w") as outfile:  
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
    
    now = datetime.now()
    dt_string = now.strftime('%Y%m%d')
    mainDict20json_Name = f'mainDict20_{dt_string}.json'
    
    with open(mainDict20json_Name, "w") as outfile:  
        json.dump(mainDict20, outfile) 
    
    
    return mainDict10json_Name, mainDict20json_Name
    
def write_mosaic(out_meta, mosaic, out_trans, folder_name, output_folder, band, key, dst_crs):

    # write the metadata of the mosaic
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": dst_crs
    })
       
    tmpname = 'mosaic_{}'.format(folder_name) # create the central folder that will contain all the mosaics
    tmppath = os.path.join(output_folder, tmpname)
    tmppathFinal = makepath(tmppath)
    mosaicfolder = os.path.join(tmppathFinal,key) # create the single folder contain the mosaic bands per single sensing date
    mosaicfolderPath = makepath(mosaicfolder) 
    mosaicName = 'S2_mosaic_{}_B{}.tiff'.format(key, band) # create the name of the mosaic image
    mosaicName_fullpath = os.path.join(mosaicfolderPath, mosaicName)
    
    with rasterio.open(mosaicName_fullpath, "w", **out_meta) as dest: # write the mosaic to geotiff
        dest.write(mosaic)
          
    print(mosaicName_fullpath)

def createMosaics (root, output_folder):
    
    Lith_foldername10 = 'Lith_output10'; Lith_foldername20 = 'Lith_output20' 
    Cy_foldername10 = 'CY_output10'; Cy_foldername20 = 'CY_output20' 
    
    dict10Name, dict20Name = get_jsons_for_mosaic(root, output_folder) 
    
    dict10 = os.path.join(root, dict10Name); dict20 = os.path.join(root, dict20Name)   
    J10 = open(dict10); J20 = open(dict20)
    dictJSON_10 = json.load(J10); dictJSON_20 = json.load(J20)
    
    for (key,value) in dictJSON_10.items(): # iterate through the dictionary 10, that contains files in 10m resolution
        for idx, subvalue in enumerate(value.values()):
            band = idx+1 # to create the band name  
            mosaicList10 = []
            for ffile in subvalue:                
                src = rasterio.open(ffile)
                mosaicList10.append(src)                    

            mosaic, out_trans = merge(mosaicList10)
            # print(out_trans)
            out_meta = src.meta.copy()
            
            if out_meta['crs'] == 'EPSG:32634': # mosaic the data of Lithuania
                write_mosaic(out_meta, mosaic, out_trans, Lith_foldername10, output_folder, band, key, dst_crs='EPSG:32634')
                
            elif out_meta['crs'] == 'EPSG:32636': # mosaic the data of Cyprus 
                write_mosaic(out_meta, mosaic, out_trans, Cy_foldername10, output_folder, band, key, dst_crs='EPSG:32636')
    
    for (key,value) in dictJSON_20.items(): # iterate through the dictionary 10, that contains the files in 20m resolution
        for idx, subvalue in enumerate(value.values()):
            band = idx+1 # to create the band name  
            mosaicList20 = [] # a list where the files to be mosaiced will be appended
            for ffile in subvalue:
                src = rasterio.open(ffile)
                mosaicList20.append(src)                    

            mosaic, out_trans = merge(mosaicList20, nodata=0, method='last')
            out_meta = src.meta.copy()
            
            if out_meta['crs'] == 'EPSG:32634':
                write_mosaic(out_meta, mosaic, out_trans, Lith_foldername20, output_folder, band, key, dst_crs='EPSG:32634')
                
            
            elif out_meta['crs'] == 'EPSG:32636':  
                write_mosaic(out_meta, mosaic, out_trans, Cy_foldername20, output_folder, band, key, dst_crs='EPSG:32636')

if __name__ == '__main__': 
    createMosaics(root, connectingFolder)
