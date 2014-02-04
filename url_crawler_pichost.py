# author: @sopier
from datetime import datetime
import pymongo

c = pymongo.Connection()
c.drop_database("urls")
db = c["urls"]

start = 1234567
end = 1652614

urls = ["http://pichost.me/" + str(i) + "/" for i in range(start, end)]

for url in urls:
    db.url.insert({
        'page': url,
        'status': 0,
        })

print db.url.find_one()
