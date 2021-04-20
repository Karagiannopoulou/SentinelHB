import os, shutil

def makepath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path

def cleanFolder(input_folder, subfolder_prefix):
    for folder in os.listdir(input_folder):
        if folder.startswith(subfolder_prefix):
            path = os.path.join(input_folder, folder)
            for subfolder in os.listdir(path):
                subfolderpath = os.path.join(path, subfolder)
                if os.path.isfile(subfolderpath):
                    os.remove(subfolderpath)
                else:
                    shutil.rmtree(subfolderpath)