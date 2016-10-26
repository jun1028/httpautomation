# -*- coding: UTF-8 -*-
# package: api.HttpClientUtil
'''

@author: Water.Zhang
'''
import StringIO
import gzip
import json
import re
import sys
import urllib
import urllib2

from log.Log import Log


try:
    import httplib
    import httplib2
except:
    print 'please install httplib2'


def callbackfunc(blocknum, blocksize, totalsize):
    '''
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
        print 'totalsize:', totalsize
    #print "%.2f%%"% percent


def download(url, filename):
    contentlen = 0
    try:
        print url, filename
        print "downloading with urllib"
        filename, header = urllib.urlretrieve(url, filename, callbackfunc)
        contentlen = header.getheader('Content-Length')
    except:
        print 'download error'
    return contentlen


class HttpClientUtil(object):
    
    _clas = 'httputil.HttpClientUtil'

    def __init__(self):
        self.headers = {}
        self.cookie = ''
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        
    def dorequest(self, url, args=None, \
                        content_type=None, \
                        methodname='POST'):
        response = None
        Log.debug(url)
        Log.debug(args)
        if methodname.upper() == 'POST':
            response = self.httppost(url, args, content_type)
        elif methodname.upper() == 'GET':
            response = self.get(url, args, content_type)
        else:
            print 'does not implement!'
        return response

    def httppost(self, url, args=None, content_type=None):
        params = urllib.urlencode(args)
        req = urllib2.Request(url, params)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = urllib2.urlopen(req)
        self.response = response
        return self.response

    def get(self, url, args=None, content_type=None):
        Log.debug('start get' + self._clas)
        if args and not isinstance(args, dict):
            args = self.strToDict(args)
        params = urllib.urlencode(args)
        url = url + '?' + params
        Log.debug(url)
        req = urllib2.Request(url)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = urllib2.urlopen(req)
        self.response = response
        Log.debug('start end' + self._clas)
        return self.response

    def openUrl(self, url, args='', content_type=''):
        req = urllib2.Request(url)
        if content_type:
            req.add_header('Content-Type', content_type)
        if isinstance(args, dict):
            body = urllib.urlencode(args)
        else:
            body = args
        response = urllib2.urlopen(req, body)
        return response

    def auth(self, url, args, username, PWD):
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, username, PWD)
        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        feedbackParams = urllib.urlencode(args)
        response = urllib2.urlopen(url + str(feedbackParams))
        return response

    def do(self, url, args, content_type='application/json', methodname='POST'):
        http = httplib2.Http()
        self.headers = {'Content-type': content_type}
        if hasattr(self, 'cookie') and len(self.cookie) > 1:
            self.headers['Cookie'] = self.cookie
        if isinstance(args, dict):
            body = urllib.urlencode(args)
        else:
            body = args
        if methodname == 'GET':
            url += '?' + body
            body = ''
        Log.debug('url:', url)
        Log.debug('methodname:', methodname)
        Log.debug('Content-type:', self.headers)
        response = http.request(url, methodname, \
                                headers=self.headers, body=body)
        return response

    def put(self, url, args, content_type=None):
        if content_type:
            return self.do(url, args, content_type, methodname='put')
        else:
            return self.do(url, args, methodname='put')

    def delete(self, url, args, content_type=None):
        if content_type:
            return self.do(url, args, content_type, methodname='delete')
        else:
            return self.do(url, args, methodname='delete')

    def post(self, url, args, content_type=None):
        if content_type:
            return self.do(url, args, content_type)
        else:
            return self.do(url, args)

    def postAndCooks(self, url, args, content_type=None):
        argDict = self.strToDict(args) 
        data = urllib.urlencode(argDict)
        urls = url.split('/')
        h = httplib.HTTPConnection(urls[2])
        path = ''
        for i in range(3, len(urls)):
            path += '/' + urls[i]
        h.request('POST', url, data, self.headers)
        r = h.getresponse()
#         print 'read', r.read()
#         print 'header', r.getheaders()
#         print 'cook', r.getheader('set-cookie')
        self.headers['Cookie'] = r.getheader('set-cookie')
#         print 'post', self.headers['Cookie'] 
        return r
    
#     def put(self, url, args, content_type=None):
#         req = urllib2.Request(url, data = urllib.urlencode(args) )
#         if content_type:
#             req.add_header('Content-Type', content_type)
#         req.get_method = lambda: 'PUT'
#         response = urllib2.urlopen(req)
#         return response
    def gzipToStr(self, data):
        data = StringIO.StringIO(data)
        gzipper = gzip.GzipFile(fileobj=data)
        html = gzipper.read()
        return html

    def strToDict(self, data):
        result = {}
        try:
            temp = re.compile(':null')
            data = temp.sub(":'result is null'", data)
            temp = re.compile(':false')
            data = temp.sub(':False', data)
            temp = re.compile(':true')
            data = temp.sub(':True', data)
            result = eval(data)
        except BaseException, e:
            print "strToDict exception"
            print e
        return result

    def strToJson(self, data):
        return json.loads(data)

    def dictToStr(self, dictData):
        strData = '{'
        for key in dictData.keys():
            temp = '"' + str(key) + '":' + '"' + dictData[key] + '"'
            if strData == '{':
                strData += temp
            else:
                strData += ','
                strData += temp
        return strData + '}'
#test
if __name__ == '__main__':
    client = HttpClientUtil()
#     try:
#         req = urllib2.Request(url)
#         res = urllib2.urlopen(req)
#         print res.read()
#     except urllib2.HTTPError as http_error:
#         import zlib
#         print zlib.decompress(http_error.read(), 30)
#     print 'd'

