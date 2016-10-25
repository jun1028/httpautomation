from log.Log import Log
import StringIO
import gzip
import json
import os
import random
import time
import hashlib
import re
import string

def gzipToStr(data):
    compressed_data = StringIO.StringIO(data)
    gzipper = gzip.GzipFile(fileobj=compressed_data)
    html = gzipper.read()
    return html

def strToGzip(uncompressed_data):
    buf = StringIO.StringIO()
    f = gzip.GzipFile(mode="wb", fileobj=buf)
    f.write(str(uncompressed_data))
    f.close()
    compressed_data = buf.getvalue()
    return compressed_data
    
def strToDict(data):
    result = {}
    try:
        if data:
            result = eval(data)
    except BaseException, e:
        Log.error("strToDict exception, ", e)
        Log.error("data is, ", data)
    return result

def strToJson(data):
    return json.loads(data)

def dictToStr(dictData):
    strData = '{'
    for key in dictData.keys():
        temp = '"' + str(key) + '":' + '"' + dictData[key] + '"'
        if strData == '{':
            strData += temp
        else:
            strData += ','
            strData += temp
    return strData + '}'

def getTime():
    timeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime())
    if timeStr[5:6] == '0':
        timeStr = timeStr[:5] + timeStr[6:]
    return timeStr

def randstr(slen):
    chars = '0123456789ABCDEF'
    rstr = ''
    for i in range(slen):
        rstr += (random.choice(chars))
        i += 1
    return rstr

def randNum(slen):
    chars = '0123456789'
    rNum = ''
    for i in range(slen):
        rNum += (random.choice(chars))
        i += 1
    return rNum

def md5(inputstr=''):
    m = hashlib.md5()   
    if inputstr:
        m.update(inputstr)
    return m.hexdigest()

def compfilesize(filename, filesize):
    result = False
    size = os.path.getsize(filename)
    if filesize == size :
        result = True
    return result

if __name__ == "__main__":
    str1 = '''{"url":"http://appport.ixingzhe.com/ouser-web/mobileLogin/loginForm.do","user":"","pwd":"5db9196dcb8049588113717558c47c91"}'''
    d1 = strToDict(str1)
    print d1
    print d1['url']
    