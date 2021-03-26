import os, shutil

def makepath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path
        
def cleanFolder(mainroot, subfolder_prefix):
    
    for folder in os.listdir(mainroot):
        if folder.startswith(subfolder_prefix):
            path = os.path.join(mainroot, folder)
            for subfolder in os.listdir(path):
                subfolderpath = os.path.join(path, subfolder)
                print(subfolderpath)
                if os.path.isfile(subfolderpath):
                    os.remove(subfolderpath)
                else:
                    shutil.rmtree(subfolderpath)