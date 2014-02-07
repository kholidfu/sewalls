import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import sys
import pymongo
from PIL import Image
from urlparse import urlparse
try:
    from imgtools.thumbnailer import Thumbnailer
    t = Thumbnailer()
except:
    sys.stdout.write('error importing')
from imagehash import average_hash


# database things
c = pymongo.Connection()
db = c["urls"]

#c.drop_database("wallpapers")
db2 = c["wallpapers"]


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

        # get fileinfo
        response = urllib2.urlopen(imgurl)
        filetype = response.info()["Content-Type"].split("/")[-1]
        filesize = response.info()["Content-Length"]

        # pastikan dulu bahwa filetype itu image
        # if blabla
        with open("/home/banteng/Desktop/pichost/" + h1 + "_" + imgurl.split("/")[-1].split(".")[0] + "." + filetype, "wb") as f:
            f.write(response.read())

        # insert into mongodb
        db2.wallpaper.insert({
            'title': h1, # full-text search
            'url': url,
            'format': filetype,
            'size': filesize,
            'added': datetime.now(),
            'hits': 0,
            'tags': h1.split() + [urlparse(url).hostname],
            'hash': average_hash(Image.open(response.read())).__str__(),
            })

    except:
        pass


# cari data secara random dari dabatase "urls" yang memiliki status 0
from random import randint
lendata = db.url.find().count()
rndnum = randint(0, lendata-10)

urls = [i['page'] for i in db.url.find({'status': 0}).skip(rndnum).limit(10)]
jobs = [gevent.spawn(phostgrab, url) for url in urls]
gevent.joinall(jobs)

# setelah itu looping urls, ubah status dari 0 menjadi 1
for url in urls:
    db.url.update({"page": url}, {"$set": {"status": 1}})

# updating data status back to 0
#>>> [db.url.update({'status': 1}, {"$set": {"status": 0}}) for i in db.url.find({'status': 1})]

# setelah itu thumbnail
# @TODO:
# auto generate folder when 10.000 images limit reached
# how to count images on each folder?

#from glob import glob
#rootdir = "/home/banteng/Desktop/thumb/"
#limc = 2

for image in os.listdir("/home/banteng/Desktop/pichost"):
    #a = glob("/home/banteng/Desktop/thumb/*")
    #b = glob("/home/banteng/Desktop/thumb/*/")
    #c = glob("/home/banteng/Desktop/thumb/*/*/*")

    try:
        im = Image.open("/home/banteng/Desktop/pichost/" + image)
        sys.stdout.write("opening image " + image + "\n")
        if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
            # create newdir
            # sebelum create dir, kita lihat dir terakhir/terbesar dulu
            # njlimet tenan, rentan error
            # os.makedirs(rootdir + "/1/" + str(int(dest.split("/")[-1]) + 1))
            # dest = "/home/banteng/Desktop/thumb/1/" + str(int(dest.split("/")[-1]) + 1)
            # resize and crop
            t.resize_and_crop(
                "/home/banteng/Desktop/pichost/" + image,
                "/home/banteng/Desktop/thumb/thumb_" + image,
                (252, 188),
                'middle')
            sys.stdout.write("thumbnailing image " + image + "\n")
    except:
        sys.stdout.write("gagal\n")
        continue

for image in os.listdir("/home/banteng/Desktop/pichost"):
    os.unlink("/home/banteng/Desktop/pichost/" + image)

sys.stdout.write("job all done!\n")
# done!
