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
i = 0

while i < 15000:
    # simple logging
    with open("/home/banteng/Desktop/log.txt", "a") as f:
        f.write("job starting from %d at %s\n" % (counter, datetime.now()))
    urls = ["http://pichost.me/" + str(i) + "/" for i in range(counter, counter + n)]
    jobs = [gevent.spawn(phostgrab, url) for url in urls]
    gevent.joinall(jobs)
    counter += n
    i += 1
    # jeda 5 detik
    with open("/home/banteng/Desktop/log.txt", "a") as f:
        f.write("jeda 5 detik\n")
    time.sleep(5)
