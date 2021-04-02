# Sentinel Hub project

INTRODUCTORY NOTES OF THE DEVELOPED SCRIPTS 
-	CreateEOPatches.py: define an AOI and create the EOpatches. This script runs once to create the first patches. It won’t be used after the first run. 
-	getEOpatches.py: this is the final script that creates the updated EOpatches changing the idx, idx_x, idx_y locations, of the wanted tiles (decrease the AOI) in order to get the data afterwards 
-	downloadData.py: download the EO data of Cyprus and Lithuania (10, 20m).
-	geotiffCreator.py: converts the np.arrays to GeoTiff, subsequently converting the zero values to NaN, and creates a file repository tree the same as the one in the mainroot directory, in order store the data in directory other than in C, avoiding space problems. The second folder can change, deciding to store the data anywhere.   
-	mosaics.py: this script creates 2 json that contains the GeoTiff files per single spectral band acquired a single date. 
-	createMultibands.py: create RGB stacks for 10m (2, 3, 4) and 20m (5, 6, 7 & 8a, 11, 12), being ready to be used for the super resolution algorithm
-	COG.py: takes the super-resolved datasets and unstack them, creating a folder per single sensing time that will contain all the single bands. Also, it converts the single-band GeoTiff images to COG
-	general_functions.py: contains the functions make path and remove data and folders. It can be used in multiple steps 
