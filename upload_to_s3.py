import os, sys
from secrets import aws_access_key_id, aws_secret_access_key, dione_s3_bucket
import boto3

main_Directory = r'D:\DIONE\WP3\SuperResolution\uploadData'


def upload_to_s3(local_imagefile, keyname):

    imageFile = open(local_imagefile, 'rb') # open and read the locally stored image file 
    bucket_folder = 'cogs/tiles-iccs'
    key_filename = "{}/{}".format(bucket_folder,keyname)      
    s3 = boto3.client(
        's3', 
        aws_access_key_id = aws_access_key_id, 
        aws_secret_access_key = aws_secret_access_key
        )
    
    s3.put_object(Bucket=dione_s3_bucket,
              Key=key_filename,
              Body=imageFile)
    
    print(key_filename)
    
    

def ingest_to_S3(input_path):
    
    for folder in os.listdir(input_path):
        full_path = os.path.join(input_path, folder)
        for subfolder in os.listdir(full_path):
            subfolder_fullpath = os.path.join(full_path, subfolder)
            for cogsFolder in os.listdir(subfolder_fullpath):
                cogsFolder_fullpath = os.path.join(subfolder_fullpath, cogsFolder)  
                if os.path.isdir(cogsFolder_fullpath):         
                    for ffile in os.listdir(cogsFolder_fullpath):
                        file_name = os.fsdecode(ffile) # decode file system
                        if file_name.endswith('cog.tiff'):
                            filename_path = os.path.join(cogsFolder_fullpath, file_name)
                            target = filename_path.split("\\")[-4:] # take the three last components of the local path to define the s3 tile
                            key_target = os.path.join(*target)
                            backslash_key_target = key_target.replace(os.sep, '/') # change the slashes to adapt to AWS file system style
                            print(backslash_key_target)
                            upload_to_s3(filename_path, backslash_key_target)
            


if __name__ == '__main__':
    ingest_to_S3(main_Directory)
