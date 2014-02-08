import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import errno
from StringIO import StringIO
import sys
import pymongo
from PIL import Image
from urlparse import urlparse
from imgtools.thumbnailer import Thumbnailer
import hashlib
import shutil
from bson.objectid import ObjectId

t = Thumbnailer()

# database things
c = pymongo.Connection()
db = c["urls"]

#c.drop_database("wallpapers")
db2 = c["wallpapers"]

import re
from unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'_'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


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

        responsebuf = response.read()

        buf = StringIO(responsebuf)
        im = Image.open(buf)

        if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
            try:
                t.resize_and_crop(
                StringIO(responsebuf),
                "/home/banteng/Desktop/temp/thumb_" + slugify(h1) + "_" + hashlib.md5(responsebuf).hexdigest() + "." + filetype,
                (252, 188),
                'middle')
                # insert into mongodb only for qualified image
                imgid = db2.wallpaper.insert({
                    'title': h1, # full-text search
                    'url': url, # unique
                    'format': filetype,
                    'size': filesize,
                    'thumb': "thumb_" + slugify(unicode(h1)) + "_" + hashlib.md5(responsebuf).hexdigest() + "." + filetype,
                    'dirname': hashlib.md5(responsebuf).hexdigest()[0] + "/" + hashlib.md5(responsebuf).hexdigest()[1:4] + "/" + hashlib.md5(responsebuf).hexdigest()[4:7],
                    'added': datetime.now(),
                    'hits': 0,
                    'tags': h1.split() + [urlparse(url).hostname],
                    'imghash': hashlib.md5(responsebuf).hexdigest(),
                    })
                sys.stdout.write("sukses inserting data\n")
                # bar iki terus di pindah ke folder yang sesuai
                # prepare for the hardest thing ...
                print 'getting data'
                imgdatasingle = db2.wallpaper.find_one({"_id": ObjectId(imgid)})
                print '\ngetting data sukses'
                print imgdatasingle["_id"]
                # create the folders [if not exist]
                try:
                    os.makedirs("/home/banteng/Desktop/thumb/" + imgdatasingle["dirname"])
                    print 'sukses membuat data'
                except OSERROR as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir("/home/banteng/Desktop/thumb/" + imgdatasingle["dirname"]):
                        print 'mboh error'
                        pass
                    else:
                        raise
                    print 'sudah ada bos'

                # move the image!
                shutil.move("/home/banteng/Desktop/temp/" + imgdatasingle["thumb"], "/home/banteng/Desktop/thumb/" + imgdatasingle["dirname"] + "/" + imgdatasingle["thumb"])

            except IOError as e:
                print e

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

# done!
