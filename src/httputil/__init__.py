# -*- coding: UTF-8 -*-
# package: api.HttpClientUtil
'''

@author: Water.Zhang
'''
import StringIO
import cookielib
import gzip
import json
import re
import sys
import urllib
import urllib2
import httplib

from log.Log import Log
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

try:
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
    return "%.2f%%"% percent


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
    headerinfo = ''

    def __init__(self):
        self.headers = {}
        #cookies
        self.cookie = ''
        self.cookies = urllib2.HTTPCookieProcessor()
        self.opener  = urllib2.build_opener(self.cookies)
    
    #调用前，需要设定header
    def dorequest1(self, url, args=None, \
                        methodname='POST'):
        response = None
        if methodname.upper() == 'POST':
            response = self.httppost(url, args)
        elif methodname.upper() == 'GET':
            response = self.get(url, args)
        else:
            print 'does not implement!'
        return response  
    
    def dorequest(self, url, args=None, \
                        content_type=None, \
                        methodname='POST'):
        response = None
        if methodname.upper() == 'POST':
            response = self.httppost(url, args, content_type)
        elif methodname.upper() == 'GET':
            response = self.get(url, args, content_type)
        elif methodname.upper() == 'UPLOAD':
            response = self.uploadfile(url, args)
        else:
            print 'does not implement!'
        return response

    def httppost(self, url, args=None, content_type=None):
        params = urllib.urlencode(args)
        req = urllib2.Request(url, params)
        if self.headers:
            req = self.setReqHeader(req, self.headers)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = self.opener.open(req)
        self.response = response
        return self.response

    def get(self, url, args=None, content_type=None, headers=None):
        params = ''
        Log.debug('start get' + self._clas)
        if args and not isinstance(args, dict):
            args = self.strToDict(args)
        if args:
            params = urllib.urlencode(args)
        if params:
            url = url + '?' + params
        Log.debug(url)
        req = urllib2.Request(url)
        if self.headers:
            req = self.setReqHeader(req, self.headers)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = self.opener.open(req)
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
#        req = urllib2.Request(url)
#         print url + str(feedbackParams)
        response = urllib2.urlopen(url + str(feedbackParams))
        return response

    def do(self, url, args, methodname='POST'):
        http = httplib2.Http()
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

    def put(self, url, args):
        return self.do(url, args, methodname='put')

    def delete(self, url, args, content_type=None):
        return self.do(url, args, methodname='delete')

    def post(self, url, args):
        return self.do(url, args, methodname='post')
        
    def setReqHeader(self, request, headers):
        for header in headers:
            request.add_header(header, headers[header])
        return request
    
    def proceHeadInfo(self, info):
        try:
            if info and 'Set-Cookie' in info:
                self.headerinfo = info
                self.cookie = info['Set-Cookie']
        except:
            Log.debug('proceHeadInfo error') 
        
    def uploadfile(self, url, filepath):
        register_openers()
        fi = open(filepath, "rb")
        datagen, headers = multipart_encode({'file': fi})
        request = urllib2.Request(url, datagen, headers)
        if self.cookie:
            self.headers['Cookie'] = self.cookie
        if self.headers:
            request = self.setReqHeader(request, self.headers)
        response = urllib2.urlopen(request)
        #response = self.opener.open(request)
        return response

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

