# -*- coding: UTF-8 -*-
# package: fixture.CommonFixture
'''
@author: water
'''
from log.Log import Log
from util.jsonutil import strToDict
import re


class CommonFixture(object):
    '''
    classdocs
    '''
    loginInfo  = {}
    preResultInfo = {}

    def __init__(self, params):
        '''
        Constructor
    
        '''
    #param: type dict {} result, 上次请求的response信息
    #param getvalueway ,从response取值的方式，=0 dict方式,=1 通过正则
    #return type dict {}
    def savePreResultInfo(self, resp):
        Log.debug('start savePreResultInfo: ' + self._CLASSNAME)
        try:
            Log.debug('start savePreResultInfo: ' + resp)
            respDict = strToDict(resp)
            Log.debug('respDict: ', respDict)
            Log.debug('needSavePreResults: ', self.needSavePreResults)
            if respDict and self.needSavePreResults.find('{') > -1:
                needSavePreResultDict = strToDict(self.needSavePreResults)
                if needSavePreResultDict:
                    Log.debug('needSavePreResultDict: ', needSavePreResultDict)
                    for key in needSavePreResultDict:
                        self.getValueFromResp(key, needSavePreResultDict[key], respDict)
                else:
                    print 'json或dictionary is error'  + self.needSavePreResults#忽略
            else:
                needSavePreResultList = self.needSavePreResults.split(';')
                for savePreResult in needSavePreResultList:
                    [key, value] = savePreResult.split('=')
#                    if respDict:
#                        self.getValueFromResp(key, value, respDict)
#                    else:
                    self.getValueFromResp(key,  value, resp)
        except BaseException, e:
            Log.error(e)
        Log.debug('end savePreResultInfo: ' + self._CLASSNAME)
        return self.preResultInfo
    
    def getValueFromResp(self, key, value, resp):
        if resp is dict and key in resp:
            self.preResultInfo[key] = resp[key]
        else:
            self.preResultInfo[key] = self.getPatternResultStr(\
                                                value, resp)
    
    def getPatternResultStr(self, pattern, resp):
        result = ''
        temp = re.findall(pattern, resp, re.IGNORECASE)
        if temp:
            #获取匹配的第一个元组
            result = temp[0].split(":")[-1]#
        return result
    
    def getneedSavePreResultkeyRe(self, value, key):
        restr = ''
        try:
            restr = '\\"' + key + '\\"' + ':' + '\\"' + value + '\\"'
        except:
            pass
        Log.debug('match re: ', restr)
        return restr

    def savePreResultInfoByRe(self, result):
        pass
    
    def savePreResultInfoByDict(self, result):
        pass
    
    def addPreResultToParams(self):
        self.setLoginInfo()
        self.addSpeficPreResultToParams()
         
    def setLoginInfo(self):
        if self.loginInfo and 'ut' in self.loginInfo:
            Log.debug("loginInfo", self.loginInfo)
            self.args['ut'] = self.loginInfo['ut']
    
    def addSpeficPreResultToParams(self):
        if hasattr(self, 'preResultInfo') and self.preResultInfo is dict:
            self.args.update(self.preResultInfo)
    
    def getUrl(self):
        #如果测试用例没有url列,或者为空，则用全局的值
        if not hasattr(self, 'url') or not self.url:
            self.url = self.interface + self.function
        return self.url
    
    #从测试文件，如excel或许excel中获取fixturename 列，并调用其run(),
    #@return result type, dict    
    def getFixture(self):
        result = {}
        if hasattr(self, 'fixturename'):
            fixturepath = self.fixturename
            fixturepath = fixturepath.strip()
            fixturename = fixturepath.split('.')[-1]
            try:
                exec 'import ' + fixturepath
                # test class method
                exec 'execfixture = ' + fixturepath + '.' + fixturename + '()' 
                result = execfixture.run()
            except BaseException, e:
                Log.error(e)
        return result
    
    def runSetupFixture(self):
        if self.setupFixture:
            fixturePath = self.setupFixture[0]
            fixtureParams = self.setupFixture[1]
            clas = fixturePath.split('.')[-1]
            try:
                exec 'import ' + clas
                exec 'fixture = ' + fixturePath + '.' + clas + '()' 
                self.initBeforeTest = fixture.run(fixtureParams)
            except BaseException, e:
                Log.error(e)
                print e
