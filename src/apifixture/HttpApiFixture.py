# -*- coding: UTF-8 -*-
# package: fixture.HttpApiFixture
'''
@author: Water.Zhang
'''

from apifixture.httpconf import DEFAULT_CONTENT_TYPE
from fixture.CommonFixture import CommonFixture
from fixture.ExcelColumnFixture import ExcelColumnFixture
from log.Log import Log
from util.jsonutil import strToDict
import re


class HttpApiFixture(ExcelColumnFixture):

    """
    templete to process http api 
    1.read excel file, process header of http request.
    2.e.g. url = interface + function..
    """
    _CLASSNAME = 'apifixture.TempleteFixture'
    note      = ''
    comments  = ['note', 'Note', 'comment', 'Comment']
    interface = ''  # http url, like http://www.xxx.com:8080/path
    function  = ''
    argCounts = 0
    setupFixture  = []
    preResultInfo = {}
    initBeforeTest = {}
    
    def processHeads(self, rowpos, ncols):
        Log.debug('start processHeads: ' + self._CLASSNAME)
        self.interface, rowpos = self.getInterface(rowpos, ncols)
        self.function, rowpos = self.getFunction(rowpos, ncols)
        self.requestMethod, rowpos = self.getRequestMethod(rowpos, ncols)
        self.content_type, rowpos = self.getContenttype(rowpos, ncols)
        Log.debug('content_type rowpos:', rowpos)
        self.auth, rowpos = self.getAuth(rowpos, ncols)
        Log.debug('auth rowpos:', rowpos)
        self.argCounts, rowpos = self.getArgCounts(rowpos, ncols)
        Log.debug('argCounts rowpos:', rowpos)
        self.setupFixture, rowpos = self.beforeTest(rowpos)
        Log.debug('beforeTest rowpos:', rowpos)
        self.note, rowpos = self.getComment(rowpos, ncols)
        Log.debug('note rowpos:', rowpos)
        Log.debug('end processHeads: ' + self._CLASSNAME)
        if not self.content_type:
            self.content_type = DEFAULT_CONTENT_TYPE
        Log.debug('content: ', self.content_type)
        return rowpos

    # @return: interface, rowpos
    def getInterface(self, rowpos, ncols):
        interface = ''
        for col in range(0, ncols):
            interface = self.excelAPP.getCellStrValue(rowpos, col)
            if len(interface) > 1 and interface.lower().find('interface') > -1:
                interface = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return interface, rowpos

    # @return: function, rowpos
    def getFunction(self, rowpos, ncols):
        function = ''
        for col in range(0, ncols):
            function = self.excelAPP.getCellStrValue(rowpos, col)
            if len(function) > 1 and function.lower().find('function') > -1:
                function = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return function, rowpos

    # @return: request, rowpos
    def getRequestMethod(self, rowpos, ncols):
        request = None
        for col in range(0, ncols):
            request = self.excelAPP.getCellStrValue(rowpos, col)
            if len(request) > 1 and request.lower().find('request') > -1:
                request = self.excelAPP.getCellStrValue(rowpos, col + 1)
                request = request.strip()
                rowpos += 1
                break
        if len(request) < 2 :
            request = None
        return request, rowpos

    # @return: request, rowpos
    def getContenttype(self, rowpos, ncols):
        content_type = ''
        for col in range(0, ncols):
            content_type = self.excelAPP.getCellStrValue(rowpos, col)
            if len(content_type) > 1 and content_type.lower().find('content') > -1:
                content_type = self.excelAPP.getCellStrValue(rowpos, col + 1)
                content_type = content_type.strip()
                rowpos += 1
                break
        return content_type, rowpos

    # @return: function, rowpos
    def getAuth(self, rowpos, ncols):
        auth = self.excelAPP.getCellStrValue(rowpos, 0)
        if len(auth) > 1 and auth.lower().find('auth') > -1:
            rowpos += 1
        return auth, rowpos

    def getPath(self, rowpos, ncols):
        request = ''
        for col in range(0, ncols):
            request = self.excelAPP.getCellStrValue(rowpos, col)
            if len(request) > 1 and request.lower().find('path') > -1:
                request = self.excelAPP.getCellStrValue(rowpos, col + 1)
                request = request.strip()
                rowpos += 1
                break
        return request, rowpos

    # @return: interface, rowpos
    def getArgCounts(self, rowpos, ncols):
        argCounts = 0
        for col in range(0, ncols):
            argCounts = self.excelAPP.getCellStrValue(rowpos, col)
            if len(argCounts) > 1 and argCounts.lower().find('argcount') > -1:
                argCounts = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return argCounts, rowpos
    
    # @return: interface, rowpos
    def beforeTest(self, rowpos):
        fixtureName = ''
        fixtureParams = ''
        for col in range(0, 2):
            temp = self.excelAPP.getCellStrValue(rowpos, col)
            if len(temp) > 1 and temp.lower().find('fixture') > -1:
                fixtureName = self.excelAPP.getCellStrValue(rowpos, col)
                fixtureParams = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return (fixtureName, fixtureParams), rowpos
    
    # @return: note, rowpos
    def getComment(self, rowpos, ncols):
        note = ''
        while True:  # multiple rows comment
            noteFlag = False
            temp = self.excelAPP.getCellStrValue(rowpos, 0)
            if len(temp) > 1:
                for comment in self.comments:
                    if temp.find(comment) > -1:
                        note = note + temp
                        noteFlag = True
                        break
            if noteFlag:
                rowpos += 1
                noteFlag = False
            else:
                break
        return note, rowpos
    
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
        self.addLoginToParams()
        self.addSpeficPreResultToParams()
         
    def addLoginToParams(self):
        if hasattr(self, 'initBeforeTest') and 'ut' in self.initBeforeTest:
            Log.debug("initBeforeTest: ", self.initBeforeTest)
            self.args['ut'] = self.initBeforeTest['ut']
    
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
            temp = fixturePath.split('.')
            clas = temp[-1]
            if len(temp) == 1:
                fixturePath = 'fixture.' + clas
            try:
                exec 'import ' + fixturePath
                exec 'fixture = ' + fixturePath + '.' + clas + '()' 
                self.initBeforeTest = fixture.run(fixtureParams)
                print self.initBeforeTest
            except BaseException, e:
                Log.error('runSetupFixture ERROR:', e)

if __name__ == "__main__":
    print 'dff'
    import fixture.LoginFixture
    