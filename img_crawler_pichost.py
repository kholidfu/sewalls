import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import pymongo
from PIL import Image

try:
    from imgtools.thumbnailer import Thumbnailer
    t = Thumbnailer()
except:
    print 'error importing'


# database things
c = pymongo.Connection()
db = c["urls"]

c.drop_database("wallpapers")
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
            'title': h1,
            'url': url,
            'filetype': filetype,
            'filesize': filesize,
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

# sementara kita kembalikan lagi ke 0
for url in urls:
    db.url.update({"status": 1}, {"$set": {"status": 0}})

# setelah itu thumbnail

for image in os.listdir("/home/banteng/Desktop/pichost"):
    try:
        im = Image.open("/home/banteng/Desktop/pichost/" + image)

        if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
            # resize and crop
            t.resize_and_crop(
                "/home/banteng/Desktop/pichost/" + image,
                "/home/banteng/Desktop/thumb/thumb_" + image,
                (250, 188),
                'middle')
    except:
        print 'gagal'
        continue

print "job all done"
# done!
