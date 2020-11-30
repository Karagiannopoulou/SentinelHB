import sys, os
import datetime as dt
import time
import numpy as np
import pickle
import geopandas
from eolearn.io import SentinelHubInputTask
from sentinelhub import CRS, BBox, DataSource, SHConfig, DataCollection, MimeType
from eolearn.io import SentinelHubInputTask
from eolearn.core import FeatureType, OverwritePermission, LinearWorkflow, SaveTask

# Credentials 
# INSTANCE_ID = '8a31a883-ce7e-48ac-a1db-43f68458ab67'
INSTANCE_ID = 'f12d5fd9-5d83-474a-a4a7-9b90adc6e27f'
CLIENT_ID = '629e3c27-b93e-4990-83d5-106707ffff1b'
CLIENT_SECRET = 's}lwWt}EUC6Irw0D7H[Cf5Q[G[]QT51aAg6|8W#%'

config = SHConfig()

try:
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID:
        config.instance_id = INSTANCE_ID
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
except:
    if config.sh_client_id == '' or config.sh_client_secret == '' or config.instance_id == '':
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")


# Set parameters for downloading the data
save = SaveTask(r'test', overwrite_permission=2, compress_level=1)

roi_bbox = BBox(bbox=[32.461853, 34.761923, 32.906799, 35.023249], crs=CRS.WGS84) # region of interest for Cyprus 
time_interval = ('2020-01-01', '2020-05-01')
maxcc = .1 # 10% maximum cloud coverage on images
# resolution of the request (in meters)
resolution = [10,20]

s2_l2a_mundi = DataCollection.define_from(DataCollection.SENTINEL2_L2A,'SENTINEL2_L2A_MUNDI',service_url='https://shservices.mundiwebservices.com')


input_task = SentinelHubInputTask(
    data_collection=s2_l2a_mundi,
    bands=['B02','B03','B04','B05','B06','B07','B08','B8A','B11','B12'],
    bands_feature=(FeatureType.DATA, 'L2A_data'),
    resolution=resolution[0],
    maxcc=maxcc,
    time_difference=dt.timedelta(hours=2),
    config=config,
    max_threads=3
)



workflow = LinearWorkflow(input_task, save)

result_bb1 = workflow.execute({input_task: {'bbox': roi_bbox, 'time_interval': time_interval},
save: {'eopatch_folder': r'test'}})

eopatch_nev = result_bb1[save]




