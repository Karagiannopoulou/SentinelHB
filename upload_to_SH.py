import os, sys
import rasterio as rio, boto3, shapely, json
from secrets import *
from fs_s3fs import S3FS 
from datetime import datetime
from shapely.geometry import box
from osgeo import ogr
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


# Your client credentials
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
# Get token for the session
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token', client_id=client_id, client_secret=client_secret)
# All requests using this session will have an access token automatically added
resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")
    

def im_read(S3_bucket_name, key_name):
    s3 = boto3.resource('s3', region_name=region)
    bucket = s3.Bucket(S3_bucket_name)
    object = bucket.Object(key_name)
    response = object.get()
    file_stream = response['Body']
    
    return file_stream    


def data_conversion_to_ingest(key_name, collection_id):
    
    tile_path = os.path.join(*key_name.split("/")[0:-1]).replace("\\","/")
    print("tile path: {}".format(tile_path))
    sensing_time = os.path.join(*tile_path.split("/")[-1:]).replace("\\","/")
    sensingTime_reformatted = datetime.strptime(sensing_time, "%Y%m%dT%H%M%S").strftime('%Y-%m-%dT%H:%M:%S') # convert datetime in format that is needed to be ingested in tile collection of SH
     
    tile = {
        'path': f'{tile_path}/(BAND).tiff',
        'sensingTime': sensingTime_reformatted
        }
    
    response = oauth.post(f'https://services.sentinel-hub.com/api/v1/byoc/collections/{collection_id}/tiles', json=tile)
    response.raise_for_status()
                                


