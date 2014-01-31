#!/usr/bin/env python
"""
Seharusnya, model aplikasi seperti ini, tidak akan memeriksa apakah
suatu image sudah ada dalam database atau belum. Kalau pun harus,
membutuhkan resource server yang luar biasa handal.

Berikut ini adalah pekerjaan2 yang akan dicron nantinya:
1. create thumbnail
2. insert database
{
title: ...,
filesize: ...,
format: ...,
added: ...,
dims: ...,
hits: ...,
tags: ...,
}
"""
import os
from PIL import Image

def create_thumb(image):
    pass

def insert_dbase(image):
    pass

def move_thumb(thumb):
    pass

if __name__ == "__main__":
    create_thumb(image)
    insert_dbase(image)
    move_thumb(image)
