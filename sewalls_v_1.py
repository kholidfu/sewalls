import urllib2
from bs4 import BeautifulSoup
import gevent

"""
duplicate detector => url link!
"""

html = urllib2.urlopen("http://megahdwallpapers.com/").read()
soup = BeautifulSoup(html)
divs = soup.findAll("div", attrs={"class": "grid_6"})
# got single link
links = [i.find("a", href=True)["href"] for i in divs]

html = urllib2.urlopen(links[0]).read()
soup = BeautifulSoup(html)

for link in links:
    html = urllib2.urlopen(link).read()
    soup = BeautifulSoup(html)
    hdpost = soup.find("div", attrs={"class": "hdpost"})
    print(hdpost.find("a", href=True)["href"])
