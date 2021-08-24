# Sentinel Hub project

SHORT NOTES OF THE DEVELOPED SCRIPTS: 
-	CreateEOPatches.py: This processing flow is used only once, in order to first create the AOIs in geoJSON, and then to generate the EOpatches. Through the EOpach generator the area is equally divided into 2400x2400 (rows, columns), and giving as a return a list with the idxs (single ids), and a bbox list (coordinates per patch). 
-  getEOpatches.py: This script was developed, as we wanted to eliminate the number of the initially created EOpatches, and thus to redefine their indexes (idx, row_id, column_id), as they have to sequentially increase. The output, which is the list of  idxs, and the bbox lists is given as an input in the EO downloader script. 
-	downloadData.py: download the EO data of Cyprus and Lithuania (10, 20m).
-	geotiffCreator.py: converts the np.arrays to GeoTiff, subsequently converting the values from 32float to 8bit integer, as this data type is requested to be ingested in the super-resolution model. Additionally, it creates an identical file repository tree with the one in the mainroot directory, in order store the data in any directory other than in C, and thus avoiding problems due to limited storage capacity. 
-	mosaics.py: In this script, single dates are found searches in all the data that were downloaded in the previous stages, and afterwards 2 json files are created containing lists with GeoTiff files per single spectral band acquired for each single date. Those lists are ingested in the write_mosaic function in order to generate the image mosaics per date. An example of the json file is given.  
-	createMultibands.py: create RGB stacks for 10m (2, 3, 4) and 20m (5, 6, 7 & 8a, 11, 12), being ready to be used for the super resolution algorithm
-	download.py: perform all the aformentioned steps to recurrently download the Sentinel-2 data. 

-	congify.py: Taking the images of either the super-resolved datasets and the drone datasets, and performing the steps of image unstacking, and conversion to Cloud optimised geotiffs.
-	upload_to_s3.py: configure the client in the AWS S3 bucket and ingest the data to the folder of the bucket.
-	upload_to_SH.py: take the data file paths from S3 bucket and perform post requests to connect the data to the Sentinel Hub data collection. 
-	upload.py: perform all the aformentioned steps to recurrently uploade the data to SH data collections. 

-	general_functions.py: contains the functions make path and remove data and folders. It can be used in multiple steps  
