import os,sys
from secrets import *
from fs_s3fs import S3FS 
from datetime import datetime
import rasterio as rio
import boto3
import shapely
from shapely.geometry import box
import json
from osgeo import ogr
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Authenticate the access in S3 bucket's filesystem
# folder of s3 bucker where the data are stored

# Your client credentials
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
# Get token for the session
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                          client_id=client_id, client_secret=client_secret)
# All requests using this session will have an access token automatically added
resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")



def access_to_S3(S3_bucket_name, aws_access_key_id, aws_secret_access_key, region):
    
    filesystem = S3FS(S3_bucket_name, # you must put only the bucket
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region=region
                  )  
        
    location_folder = s3_folder
    
    return filesystem, location_folder

def im_read(S3_bucket_name, key_name):
    s3 = boto3.resource('s3', region_name=region)
    bucket = s3.Bucket(S3_bucket_name)
    object = bucket.Object(key_name)
    response = object.get()
    file_stream = response['Body']
    return file_stream    

                    
def ingest_to_SH():
      
    filesystem, location_on_bucket = access_to_S3(dione_s3_bucket, aws_access_key_id, aws_secret_access_key, region) 
      
  
    for folder in filesystem.listdir(location_on_bucket):
        fullpath= os.path.join(location_on_bucket, folder).replace("\\","/") # replace windows slashs to backslash, to be fitted with S3 filesystem.  
        for subfolder in filesystem.listdir(fullpath):
            subfolder_fullpath = os.path.join(fullpath, subfolder).replace("\\","/")
            if subfolder_fullpath.endswith('Cyprus/Sentinel2'):
                for sensingTime in filesystem.listdir(subfolder_fullpath):
                    sensingTime_reformatted = datetime.strptime(sensingTime, "%Y%m%dT%H%M%S").strftime('%Y-%m-%dT%H:%M:%S') # convert datetime in format that is needed to be ingested in tile collection of SH
                    innerfolder_fullpath = os.path.join(subfolder_fullpath, sensingTime).replace("\\","/")
                    for band in filesystem.listdir(innerfolder_fullpath):
                        raster_path = os.path.join(innerfolder_fullpath, band).replace("\\","/")
                        key_name = os.path.join(*raster_path.split("/")[1:]).replace("\\","/")
                        im = im_read(dione_s3_bucket, key_name)
                        with rio.open(im) as src:
                            crs = src.crs
                            crs_urn = f'urn:ogc:def:crs:EPSG::{str(crs).split(":")[-1]}' # transform to urn format
                            bounds = src.bounds
                        geom = box(*bounds)
                        wkt = geom.wkt
                        geom = ogr.CreateGeometryFromWkt(wkt)
                        cover_geometry = json.loads(geom.ExportToJson()) 
                        print(cover_geometry) 
                        sys.exit()                      
                        
                        tile = {
                            'path': 'cogs/tiles-iccs/Cyprus/Sentinel2/20200428T082601/B11_cog.tiff',
                            'sensingTime': sensingTime_reformatted,
                            'coverGeometry': cover_geometry
                            }
                        
                        response = oauth.post(f'https://services.sentinel-hub.com/api/v1/byoc/collections/63fa7e3f-e044-4e08-bc45-c5132fabdb22/tiles', json=tile)
                        print(response.raise_for_status())
                        
                            
                            
                         

    


if __name__ == '__main__':
    ingest_to_SH()

