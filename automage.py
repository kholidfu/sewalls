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

import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
# non-fatigue robots :)
import time
from datetime import datetime

def phostgrab(url):
    """fungsi ini akan mendownload 10 image tiap kali dijalankan."""
    try:
        req = urllib2.Request(url, headers={
        "Referer": "http://pichost.me",
        "User-agent": "Mozilla/5.0",
        })
        html = urllib2.urlopen(req).read()
        soup = BeautifulSoup(html)
        h1 = soup.find("h1").getText().replace(" ", "_").lower()
        div = soup.find("div", attrs={"class": "box1"})

        # this is full-path url to download
        imgurl = div.find("a", href=True)["href"]

        # get file info
        response = urllib2.urlopen(imgurl)
        filetype = response.info()["Content-Type"].split("/")[-1]
        filesize = response.info()["Content-Length"]

        # writing to file
        with open("/home/banteng/Desktop/pichost/" + h1 + "_" + imgurl.split("/")[-1].split(".")[0] + "." + filetype, "wb") as f:
            f.write(response.read())
    except:
        pass


counter = 1234567
# jumlah data tiap sekali jalan
n = 100

while True:
    # simple logging
    with open("/home/banteng/Desktop/log.txt", "a") as f:
        f.write("job starting from %d at %s\n" % (counter, datetime.now()))
    urls = ["http://pichost.me/" + str(i) + "/" for i in range(counter, counter + n)]
    jobs = [gevent.spawn(phostgrab, url) for url in urls]
    gevent.joinall(jobs)
    counter += n
    # jeda 5 detik
    with open("/home/banteng/Desktop/log.txt", "a") as f:
        f.write("jeda 5 detik\n")
    time.sleep(5)


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
