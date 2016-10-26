'''
@author: water
'''
from httputil import HttpClientUtil
from log.Log import Log
from util import strToDict


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
    def login(self, params):
        result = ''
        if type(params) == str or type(params) == unicode:
            print params
            params = strToDict(params)
            if 'url' in params:
                url = params.pop('url')
                if 'needreturnkey' in params:
                    needreturnkey = params.pop('needreturnkey')
                else:
                    needreturnkey = self.defaultneedreturnkey
                url = 'http://' + url
                print url
                resp = self.client.dorequest(url, params, \
                                                 methodname='post')
                respdata = resp.read()
                print respdata
                jsonResult = strToDict(respdata)
                if jsonResult and needreturnkey in jsonResult:
                    result = jsonResult[needreturnkey]
        return result
    
    def getToken(self, jsonResult):
        if jsonResult and 'data' in jsonResult:
            data = jsonResult["data"]
            token = data["token"]
            Log.debug("token is ",  token)
            return token
        else:
            return None