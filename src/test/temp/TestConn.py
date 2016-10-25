# -*- coding: UTF-8 -*-
'''

@author: Water
'''

import httplib
conn = httplib.HTTPConnection("61.147.88.121", 28083)
print 'conn'
conn.request("GET", "/filter-api-1.0-SNAPSHOT/crawler?song=hellothddatdsd   ddisgodsdfhff  dfdf fgf sds d")
rsps = conn.getresponse()
#print rsps.getheaders()
print rsps.status
print rsps.version
data = rsps.read()
print  data
conn.close()
exec "tt = 'dd'"
# print tt 505 http version

if __name__ == '__main__':
    pass