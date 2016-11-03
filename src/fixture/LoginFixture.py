# -*- coding: UTF-8 -*-
'''
@author: water
'''
from httputil import HttpClientUtil
from log.Log import Log
from util.jsonutil import strToDict
import re
import sys


class LoginFixture(object):
    '''
    classdocs
    '''
  
    def __init__(self):
        '''
        Constructor
        '''
        self.client = HttpClientUtil()
        self.defaultneedreturnkey = 'ut'
    
    #@params type:dict key: 'url', 'username'
    #   sample     params = {'url':url, 'username':username,'pwd':pwd}
    #@return type:dict key: "ut"
    #   sample     loginResult = {"ut":ut}
    def run(self, params, returnparam=None):
        result = {}
        tokenvalue = ''
        cookie = ''
        if type(params) == str or type(params) == unicode:
            params = strToDict(params)
            if 'url' in params:
                if params['url'].find("http") < 0:
                    url = 'http://'  + params.pop('url')
                else:
                    url = params.pop('url')
                resp = self.client.dorequest(url, params, \
                                                 methodname='post')
                if not resp:
                    print 'login fail, test over!' 
                    sys.exit()
                respdata = resp.read()
                if not respdata:
                    print 'login fail, respdata is null!' 
                    sys.exit()
                cookie = self.getCookie(resp.info())
                if cookie:
                    result['cookie'] = cookie
                tokenvalue = self.getToken(respdata, returnparam)
                if tokenvalue:
                    result['token'] = tokenvalue
        return result
    
    def getCookie(self, info):
        cookie = ''
        try:
            if info and 'Set-Cookie' in info:
                cookie = info['Set-Cookie']
        except BaseException, e:
            Log.error("get cookie value error", e)  
        return cookie
                
    def getToken(self, respdata, returnparam):
        tokenvalue = ''
        try:
            jsonResult = strToDict(respdata)
            if not returnparam:
                if jsonResult and 'data' in jsonResult:
                    data = jsonResult["data"]
                    tokenvalue = data["token"]
                else:
                    tokenvalue = re.findall(returnparam, respdata, re.IGNORECASE)[0]
                    tokenvalue = tokenvalue.split(":")[-1]
            else:
                if returnparam in jsonResult:
                    tokenvalue = jsonResult[returnparam]
                else:
                    #re.findall
                    tokenvalue = re.findall(returnparam, respdata, re.IGNORECASE)[0]
                    tokenvalue = tokenvalue.split(":")[-1]
        except BaseException, e:
            Log.error("get token value error", e)  
        Log.debug("token is ",  tokenvalue)
        return tokenvalue