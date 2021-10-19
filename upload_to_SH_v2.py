import os, sys
from secrets import *
from datetime import datetime
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session

# Your client credentials
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
# Create a session
oauth = OAuth2Session(client=BackendApplicationClient(client_id=client_id))
# Get token for the session
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token', client_id=client_id, client_secret=client_secret)
# All requests using this session will have an access token automatically added


def data_conversion_and_ingest(key_name, collection_id):
    
    tile_path = os.path.join(*key_name.split("/")[0:-1]).replace("\\","/")
    print("tile path: {}".format(tile_path))
    sensing_time = os.path.join(*tile_path.split("/")[-1:]).replace("\\","/")
    sensingTime_reformatted = datetime.strptime(sensing_time, "%Y%m%dT%H%M%S").strftime('%Y-%m-%dT%H:%M:%S') # convert datetime in format that is needed to be ingested in tile collection of SH
     
    tile = {
        'path': f'{tile_path}/(BAND).tiff',
        'sensingTime': sensingTime_reformatted
        }
    
    try:
        response = oauth.post(f'https://services.sentinel-hub.com/api/v1/byoc/collections/{collection_id}/tiles', json=tile)
        response.raise_for_status()
    
    except TokenExpiredError as e:
        print("Token expired. Perform the request again!")
        
        client = OAuth2Session(client=BackendApplicationClient(client_id=client_id))
        token2 = client.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token', client_id=client_id, client_secret=client_secret)
        response = client.post(f'https://services.sentinel-hub.com/api/v1/byoc/collections/{collection_id}/tiles', json=tile)
        

                                  

if __name__ == '__main__':
    data_conversion_and_ingest()


