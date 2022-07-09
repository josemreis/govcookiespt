import tarfile
import shutil
import os
from typing import Optional
import requests

## compress dirs or files
def _tar(files: Optional[list]) -> None:
    if files:
        is_file = False
        for f in files:
            if os.path.isfile(f) and "tar" not in f:
                files = [f]
                is_file = True
            elif os.path.isdir(f) and "tar" not in f:
                files = [os.path.join(f, _f) for _f in os.listdir(f)]
            else:
                continue
            tar_filename = f + ".tar.gz"
            tar = tarfile.open(tar_filename, "w:gz")
            for name_ in files:
                tar.add(name_, os.path.basename(name_))
            tar.close()
            if is_file:
                os.remove(f)
            else:
                shutil.rmtree(f)

def current_location():
    """Given the public IP fetch the current location"""
    # get the current ip
    pubip = requests.get("https://ipinfo.io/ip").text
    return requests.get(f"https://ipinfo.io/{pubip}").json()["country"]
