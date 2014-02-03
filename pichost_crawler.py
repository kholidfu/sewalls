import gevent
from gevent import monkey
monkey.patch_all()
import urllib2
from bs4 import BeautifulSoup
# non-fatigue robots :)
import time
from datetime import datetime

import pymongo
c = pymongo.Connection()
c.drop_database("urls")
db = c["urls"]

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

        # insert into mongodb
        db.url.insert({
            'page': url,
            'fullpath': imgurl,
            'status': 0
            })
    except:
        pass


counter = 1234567
end = 1652614
# jumlah data tiap sekali jalan
n = 100
i = 0

while i < 1234670:
    urls = ["http://pichost.me/" + str(i) + "/" for i in range(counter, counter + n)]
    jobs = [gevent.spawn(phostgrab, url) for url in urls]
    gevent.joinall(jobs)
    counter += n
    i += 1
    # jeda 5 detik
    time.sleep(5)

print db.url.find_one()
