#!/usr/bin/env python
"""
Proses:
1. get 15000 images
2. upload to online storage service (opsional)
3. create thumb and insert into dbase
4. del big images

Note:
Ukuran image besar 15000 image == 5.6GB
ukuran thumbnail 15000 image ukuran 250 width == 120MB
Berarti untuk 160GB image besar, hanya butuh ~ 3.5GB
"""

import os
from PIL import Image

def automage():
    """
    1. mass download 15000 files
    2. upload to online storage
    3. create thumb + insert into dbase
    4. delete the real images.
    """
    pass

if __name__ == "__main__":
    automage()
