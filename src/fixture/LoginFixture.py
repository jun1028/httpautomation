'''
@author: water
'''
from httputil import HttpClientUtil
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
            params = strToDict(params)
            if 'url' in params:
                url = params.pop('url')
                if 'needreturnkey' in params:
                    needreturnkey = params.pop('needreturnkey')
                else:
                    needreturnkey = self.defaultneedreturnkey
                resp = self.client.dorequest(url, params, \
                                                 methodname='post')
                respdata = resp.read()
                jsonResult = strToDict(respdata)
                if needreturnkey in self.jsonResult:
                    result = jsonResult[needreturnkey]
        return result