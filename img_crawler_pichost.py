import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
from StringIO import StringIO
import sys
import pymongo
from PIL import Image
from urlparse import urlparse
from imgtools.thumbnailer import Thumbnailer
import hashlib

t = Thumbnailer()

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

        #print average_hash(Image.open(StringIO(response.read()))).__str__()
        # pastikan dulu bahwa filetype itu image
        # if blabla
        #with open("/home/banteng/Desktop/pichost/" + h1 + "_" + imgurl.split("/")[-1].split(".")[0] + "." + filetype, "wb") as f:
        #f.write(response.read())

        try:
            buf = StringIO(response.read())
            im = Image.open(buf)
        except:
            print 'error opening image'

        if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
            try:


                t.resize_and_crop(
                    StringIO(urllib2.urlopen(imgurl).read()),
                    "/home/banteng/Desktop/thumb_" + h1 + filetype,
                    (252, 188),
                    'middle')
            except IOError as e:
                print e

        # insert into mongodb
        db2.wallpaper.insert({
            'title': h1, # full-text search
            'url': url, # unique
            'format': filetype,
            'size': filesize,
            'added': datetime.now(),
            'hits': 0,
            'tags': h1.split() + [urlparse(url).hostname],
             'imghash': hashlib.md5(response.read()).hexdigest(),
            })

        sys.stdout.write("sukses inserting data\n")

    except:
        pass


# cari data secara random dari dabatase "urls" yang memiliki status 0
from random import randint
lendata = db.url.find().count()
rndnum = randint(0, lendata-10)

urls = [i['page'] for i in db.url.find({'status': 0}).skip(rndnum).limit(5)]
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

# for image in os.listdir("/home/banteng/Desktop/pichost"):
#     try:
#         im = Image.open("/home/banteng/Desktop/pichost/" + image)
#         sys.stdout.write("opening image " + image + "\n")
#         if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
#             t.resize_and_crop(
#                 "/home/banteng/Desktop/pichost/" + image,
#                 "/home/banteng/Desktop/thumb/thumb_" + image,
#                 (252, 188),
#                 'middle')
#             sys.stdout.write("thumbnailing image " + image + "\n")
#     except:
#         sys.stdout.write("gagal\n")
#         continue
#
#
#
# for image in os.listdir("/home/banteng/Desktop/pichost"):
#     os.unlink("/home/banteng/Desktop/pichost/" + image)
#
# sys.stdout.write("job all done!\n")
# done!
