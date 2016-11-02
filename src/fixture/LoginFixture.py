'''
@author: water
'''
from httputil import HttpClientUtil
from log.Log import Log
from util.jsonutil import strToDict


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
    def run(self, params):
        jsonResult = {}
        if type(params) == str or type(params) == unicode:
            params = strToDict(params)
            if 'url' in params:
                url = 'http://'  + params.pop('url')
                resp = self.client.dorequest(url, params, \
                                                 methodname='post')
                respdata = resp.read()
                jsonResult = strToDict(respdata)
        return jsonResult
    
    def getToken(self, jsonResult):
        tokenvalue = ''
        if jsonResult and 'data' in jsonResult:
            data = jsonResult["data"]
            tokenvalue = data["token"]
            Log.debug("token is ",  tokenvalue)
        return tokenvalue