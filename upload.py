#!/usr/bin/env python
# Default libs
import sys
import os

# Geospatial libraries
import json
import ogr
import rasterio
from shapely import wkt
import geopandas as gpd
import shapely

# Auxiliary libraries
from fs_s3fs import S3FS # pyfilesystem interface to having access in Amazon S3 bucket
from dateutil import parser
from datetime import datetime
import subprocess

# Authorization/Authentication libraries
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Your client credentials
client_id = ''
client_secret = ''

# Fetch an access token from the provider
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Get token for the session
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                          client_id=client_id, client_secret=client_secret)
# All requests using this session will have an access token automatically added
resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")

# Global variables 
mainDirectory = r'.\COG'
collection_id2 = '51353d22-2ae7-4613-b154-1540a8bcc90c'

# Data collection id
def collection(name, s3Bucket):  
    
    collection = {
      'name': name ,
      's3Bucket': s3Bucket 
    }
    
    response = oauth.post('https://services.sentinel-hub.com/api/v1/byoc/collections', json=collection)
    response.raise_for_status()
    
    collection = json.loads(response.text)['data']
#     collection = json.loads(response.text)['data']
#     collection_id = collection['id']
    if collection['id'] == collection_id2:
        
        
        print(collection['id'])
    
    
# def tile():
        
    
        









if __name__ == '__main__':
    collection('superResolved', 'superresolved2')
    



