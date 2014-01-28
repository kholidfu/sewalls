import urllib2
from bs4 import BeautifulSoup
import gevent
import json
import pymongo

"""
duplicate detector => url link!
"""

html = urllib2.urlopen("http://megahdwallpapers.com/").read()
soup = BeautifulSoup(html)
divs = soup.findAll("div", attrs={"class": "hdpost"})
# got single link
links = [i.find("a", href=True)["href"] for i in divs]

html = urllib2.urlopen(links[0]).read()
soup = BeautifulSoup(html)

d = {}

c = pymongo.Connection()
c.drop_database('wallpapers')
db = c['wallpapers']

for link in links:
    html = urllib2.urlopen(link).read()
    soup = BeautifulSoup(html)
    hdpost = soup.find("div", attrs={"class": "hdpost"})
    d.update({"url": hdpost.find("a", href=True)["href"]})
    d.update({"status": 0})
    #print(json.dumps(d))
    db.wallpaper.insert(d)

print(db.wallpaper.find_one())

# output example:
"""
{"url": "http://megahdwallpapers.com/wp-content/uploads/2014/01/office-girl-in-black-dress-and-stockings-wide-screen-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2014/01/deepika-padukone-cute-in-shirt-wide-monitor-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/12/sonakshi-sinha-gorgeous-in-white-dress-2014-wide-screen-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/12/anushka-sharma-cute-in-pink-dress-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/12/dhoom-3-katrina-kaif-skin-color-dress-wide-screen-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/12/deepika-padukone-and-ranveer-singh-ram-leela-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/12/shruti-hassan-cute-girl-wide-screen-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/11/deepika-padukone-latest-2014-wide-screen-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/11/telugu-actress-kajal-aggarwal-cute-actress-hd-wallpaper.jpg", "status": 0}
{"url": "http://megahdwallpapers.com/wp-content/uploads/2013/11/shraddha-kapoor-desi-look-wide-monitor-hd-wallpaper.jpg", "status": 0}
"""


# data ini kemudian masuk antrian di downloader script, setelah download
# sukses, status dirubah menjadi 1
