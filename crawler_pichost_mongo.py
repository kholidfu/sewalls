import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
import os
from StringIO import StringIO
import pymongo
from gridfs import GridFS
from PIL import Image
from urlparse import urlparse
from imgtools.thumbnailer import Thumbnailer
import shutil
import re
from unidecode import unidecode

t = Thumbnailer()

# database things
c = pymongo.Connection()
db = c["urls"]

#c.drop_database("wallpapers")
db2 = c["wallpapers"]
# activate gridfs
fs = GridFS(db2)

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
        filetype = response.info()["Content-Type"]
        filesize = response.info()["Content-Length"]

        responsebuf = response.read()

        buf = StringIO(responsebuf)
        im = Image.open(buf)

        if im.size[0] >= 1920 and im.size[0]/float(im.size[1]) >= 1.6:
            try:
                t.resize_and_crop(
                StringIO(responsebuf),
                "/home/banteng/Desktop/temp/thumb_" + slugify(h1) + "." + filetype.split("/")[-1],
                (252, 188),
                'middle')
                # bar diresize terus di open
                with open("/home/banteng/Desktop/temp/thumb_" + slugify(h1) + "." + filetype.split("/")[-1]) as f:
                    # insert into mongodb only for qualified image
                    oid = fs.put(f,
                           content_type=filetype,
                           title=h1,
                           url=url,
                           imgformat=filetype.split("/")[-1],
                           size=filesize,
                           hits=0,
                           tags=h1.split() + [urlparse(url).hostname],
                           )
                # os.unlink("/home/banteng/Desktop/temp/thumb_" + slugify(h1) + "." + filetype.split("/")[-1])

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
# looping = [i for i in db.fs.files.find()]
# done!
