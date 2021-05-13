import os, sys
from secrets import aws_access_key_id, aws_secret_access_key, dione_s3_bucket
import boto3


def upload_to_s3(local_imagefile, keyname):

    imageFile = open(local_imagefile, 'rb') # open and read the locally stored image 
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
    
    return key_filename


def ingest_to_S3(ffile):
    filename_path = os.fsdecode(ffile) # decode file system because it contains only numbers
    if filename_path.endswith('cog.tiff'):
        target = filename_path.split("\\")[-4:] # take the three last components of the local path to define the s3 tile
        key_target = os.path.join(*target)
        backslash_key_target = key_target.replace(os.sep, '/') # change the slashes to adapt to AWS file system style
        ingested_image = upload_to_s3(filename_path, backslash_key_target)
        
        return ingested_image

