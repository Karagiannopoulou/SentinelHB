# Default libs
import sys, os, shutil, json
import time, schedule 

# Basics of GIS
from general_functions import makepath
from datetime import datetime

#custom functions
from secrets import *
from congify import split, create_single_band_image_Sentinel, create_single_band_image_drones, cognify_image
from upload_to_s3 import ingest_to_S3
from upload_to_SH import data_conversion_to_ingest
 
# Global vars
# main_Directory = r'D:\DIONE\WP3\SuperResolution\uploadData' # test 
main_Directory = r'Z:\EU_PROJECTS\DIONE\WP3\SuperResolution\uploadData' # final data storage

def unstack_image_and_cognify(input_path):
    
    # path: # as we build the file structure both in the root folder and the output folder, 
    # we isolate the folder path from the root and pasted to a variable that depicts the output folder
    ingested_drones_lithuania = []; ingested_S2_lithuania = []; ingested_drones_cyprus = []; ingested_S2_cyprus = []
    json_drones = {}; json_s2 = {}
    
    for folder in os.listdir(input_path):
        full_path = os.path.join(input_path, folder)
        for subfolder in os.listdir(full_path):
            if 'drones' in subfolder:
                subfolder_fullpath = os.path.join(full_path, subfolder)
                for ffile in os.listdir(subfolder_fullpath):
                    file_name = os.fsdecode(ffile) # decode file system
                    filename_path = os.path.join(subfolder_fullpath, file_name)                
                    if filename_path.endswith('.tiff') or file_name.endswith('.tif'):
                        print(filename_path)
                        name = os.path.splitext(os.path.basename(filename_path))[0]
                        name_in_moved_file = r"{}\uploaded\{}.tiff".format(subfolder_fullpath,name) # create location file path to move the file there
                        sensing_time = name.split("_")[-1] 
                        tileFolder_Name = os.path.join(subfolder_fullpath,sensing_time)
                        tile_folder = makepath(tileFolder_Name)                     
                        band_name_list, outputband_list = create_single_band_image_drones(filename_path,tile_folder) # unstack the images
                        shutil.move(filename_path, name_in_moved_file) # move the RGB multiband file as it isn't needed for the next steps
                        for band_name, outputband in zip(band_name_list, outputband_list):  # use the two list mentioned before to congify the images            
                            cog_file = cognify_image(outputband, tile_folder, band_name, blocksize=2048, nodata=None) # congify single band images and print the output filename
                            ingested_file = ingest_to_S3(cog_file) # take the output COG image and ingest it to s3 bucket
                            if 'Cyprus' in ingested_file:
                                ingested_drones_cyprus.append(ingested_file)
                            elif 'Lithuania' in ingested_file:
                                ingested_drones_lithuania.append(ingested_file)
                               
                      
            
            elif 'Sentinel2' in subfolder:
                subfolder_fullpath = os.path.join(full_path, subfolder)         
                for ffile in os.listdir(subfolder_fullpath):
                    file_name = os.fsdecode(ffile) # decode file system
                    if file_name.endswith('.tiff') or file_name.endswith('.tif'):
                        filename_path = os.path.join(subfolder_fullpath, file_name) # initial file path of the image
                        print("filename_path: {}".format(filename_path))
                        name = os.path.splitext(os.path.basename(filename_path))[0]
                        name_in_moved_file = r"{}\uploaded\{}.tiff".format(subfolder_fullpath,name) # upload file name
                        sensing_time = name.split("_")[-1] # take the time of the image
                        rgbName = name.split("_")[1] # take the rgb of the image
                        rgbBand_list = split(rgbName) # split the part of the name showing the bands e.g. 567 and include them into a list
                        tileFolder_Name = os.path.join(subfolder_fullpath,sensing_time)
                        tile_folder = makepath(tileFolder_Name)
                        
                        if (len(rgbName)%2)==1 and rgbName in filename_path: # if the list of the length is an uneven number then include in band names 5,6,7 bands and create the folder with sensing time as a name 
                            band_name_list, outputband_list = create_single_band_image_Sentinel(filename_path,rgbBand_list,tile_folder)
                            shutil.move(filename_path, name_in_moved_file)
                            for band_name, outputband in zip(band_name_list, outputband_list): 
                                cog_file = cognify_image(outputband, tile_folder, band_name, blocksize=2048, nodata=None)
                                ingested_file = ingest_to_S3(cog_file)
                                if 'Cyprus' in ingested_file:
                                    ingested_S2_cyprus.append(ingested_file)
                                elif 'Lithuania' in ingested_file:
                                    ingested_S2_lithuania.append(ingested_file) # append only once as I don't care to have all the bands, as I only want the s3 folder name 
                            
                         
                        elif (len(rgbName)%2)==0 and rgbName in filename_path: # if the length of the list is even (e.g. 8a, 11, 12) the folder exists, so go to the same folder an create the bands 8a, 11, 12
                            band_name_list, outputband_list = create_single_band_image_Sentinel(filename_path,rgbBand_list, tile_folder)
                            shutil.move(filename_path, name_in_moved_file)
                            for band_name, outputband in zip(band_name_list, outputband_list): 
                                cog_file = cognify_image(outputband, tile_folder, band_name, blocksize=2048, nodata=None)
                                ingested_file = ingest_to_S3(cog_file)                                
                        
                
    json_drones = {'Cyprus': ingested_drones_cyprus, 'Lithuania':ingested_drones_lithuania}
    print(json_drones)
        
    with open('json_drones.json', "w") as outfile:  
        json.dump(json_drones, outfile) 
     
    json_json_s2 = {'Cyprus': ingested_S2_cyprus, 'Lithuania':ingested_S2_lithuania}
    print(json_json_s2)
     
    with open('json_s2.json', "w") as outfile:
        json.dump(json_json_s2, outfile)           
    

def ingest_to_SH(json_drones, json_s2):
    
    J_drones = open(json_drones); J_s2 = open(json_s2)
    dictJSON_drones = json.load(J_drones); dictJSON_s2 = json.load(J_s2)
    
    for dr_key,dr_values in dictJSON_drones.items():
        for dr_image in dr_values:
            if dr_image.endswith('B1_cog.tiff') and dr_key=='Cyprus':
#                 print('location {}, images {}'.format(dr_key, dr_image))
                data_conversion_to_ingest(dr_image, collection_id_Cyprus_dr)
            elif dr_image.endswith('B1_cog.tiff') and dr_key=='Lithuania':
#                 print('location {}, images {}'.format(dr_key, dr_image))
                data_conversion_to_ingest(dr_image, collection_id_Lithuania_dr)
           

    for s2_key,s2_values in dictJSON_s2.items():
        for s2_image in s2_values:
            if s2_image.endswith('B5_cog.tiff') and s2_key=='Cyprus':
#                 print('location {}, images {}'.format(s2_key, s2_image))
                data_conversion_to_ingest(s2_image, collection_id=collection_id_Cyprus_s2)
            elif s2_image.endswith('B5_cog.tiff') and s2_key=='Lithuania':
#                 print('location {}, images {}'.format(s2_key, s2_image))
                data_conversion_to_ingest(s2_image, collection_id=collection_id_Lithuania_s2)


def uploader():
    unstack_image_and_cognify(main_Directory)
    ingest_to_SH(r'.\json_drones.json', r'.\json_s2.json')
    print(datetime.now())
      
      
def main():
    uploader()
    schedule.every(2).days.do(uploader) 
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
