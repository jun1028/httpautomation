'''
@author: water
'''
from httputil import HttpClientUtil
from log.Log import Log
from util.jsonutil import strToDict
import re


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
        tokenvalue = ''
        if type(params) == str or type(params) == unicode:
            params = strToDict(params)
            if 'url' in params:
                if params['url'].find("http") < 0:
                    url = 'http://'  + params.pop('url')
                else:
                    url = params.pop('url')
                resp = self.client.dorequest(url, params, \
                                                 methodname='post')
                
                respdata = resp.read()
                print respdata
                tokenvalue = self.getToken(respdata, returnparam)
        print tokenvalue
        return tokenvalue
    
    def getToken(self, respdata, returnparam):
        tokenvalue = ''
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
                #re.findall ·µ»ØÒ»¸ölist,
                tokenvalue = re.findall(returnparam, respdata, re.IGNORECASE)[0]
                tokenvalue = tokenvalue.split(":")[-1]
        Log.debug("token is ",  tokenvalue)
        return tokenvalue