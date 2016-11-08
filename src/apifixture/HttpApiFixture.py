# -*- coding: UTF-8 -*-
# package: fixture.HttpApiFixture
'''
@author: Water.Zhang
'''

from apifixture import LOGFIELPATH
from apifixture.httpconf import DEFAULT_CONTENT_TYPE
from check.result_check import ResultCheck
from django.core.files import temp
from fixture.ExcelColumnFixture import ExcelColumnFixture
from httputil import HttpClientUtil
from log.Log import Log
from urllib2 import HTTPError
from util.jsonutil import strToDict, strToJson
import os
import re


class HttpApiFixture(ExcelColumnFixture):

    """
    process http api 
    1.read excel file, process header of http request.
    2.e.g. url = interface + function..
    """
    _CLASSNAME = 'apifixture.HttpApiFixture'
    note      = ''
    comments  = ['note', 'Note', 'comment', 'Comment']
    interface = ''  # http url, like http://www.xxx.com:8080/path
    function  = '' #path
    argCounts = 0 #
    initSetupFixture  = [] #在测试运行前需要执行的测试构建的【构建名，构建参数】
    preResultInfo = {} #前一次请求response的需要保存的结果信息
    client = HttpClientUtil() #客户端请求
    previousResp = None  #前一次请求的response
    link = ''
    userdefinefixtureresult = None #测试执行过程中测试构建执行的测试结果信息
    reqargs = {} #http请求参数
    initInfoBeforeTest = {}
    
    def runTest(self, cell, a):
        Log.debug('start runTest: ' + self._CLASSNAME)
        try:
            if not self.expected:
                self.expected = a.parse(cell.text)
        except BaseException, e:
            Log.debug("testcaseid " + str(self.testCaseId))  
            Log.debug(e)
            self.expected = ''
        try:
            actualresult = a.get() #调用测试构建定义的方法
            try:
                #self.needSavePreResults用于保存上次请求response需要保存的测试字段值，不同字段用“，”分割；可用正则或完成字段名，
                if hasattr(self, 'needSavePreResults') and self.needSavePreResults:
                    self.preResultInfo = {} #clear上次保存的信息
                    self.savePreResultInfo(actualresult)
                Log.debug('preResultInfo', self.preResultInfo)
            except BaseException, e:
                Log.error('invoke savePreResultInfo error', e)
            if self.expected and actualresult:
                bresult, message = ResultCheck.checkResult(actualresult, self.expected)
            else:
                if actualresult and actualresult.find('error') < 0:
                    bresult = 1
                    message = "expect result column is null, only output!\n"
                else:
                    bresult = 0
                    message = "expect result column is null, maybe error!\n the url:%s \n" % self.url
            if bresult > 0:
                self.right(cell, message)
            elif bresult == 0:
                self.wrong(cell, message)
            else:
                self.output(cell, message)
            try:
                cell.text = cell.text + self.link
            except:
                cell.text = self.link
        except BaseException, e:
            self.exception(cell, e)
            Log.exception(e)
        Log.debug('end runTest: ' + self._CLASSNAME)
    
    def doRequest(self, url, reqargs, requestMethod):
        respData = None
        #开始HTTP请求
        try:
            resp = self.client.dorequest(url, reqargs, \
                                         methodname=requestMethod)
            if self.url.find('login') > -1: #如果是一个登陆的url
                self.initInfoBeforeTest['cookie'] = self.client.getCookie(resp.info())
            if isinstance(resp, str):
                respData = resp
            else:
                respData = resp.read()
            Log.debugvar('respData is ', respData)
        except HTTPError, e:
            respData = '{"error":"' + str(e) + '"}'
        except Exception, e:
            respData = '{"error":"' + str(e) + '"}'
        self.previousResp = respData
        return respData
    
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
        self.initSetupFixture, rowpos = self.getInitSetupFixture(rowpos)
        Log.debug('initBeforeTest rowpos:', rowpos)
        self.note, rowpos = self.getComment(rowpos, ncols)
        Log.debug('note rowpos:', rowpos)
        Log.debug('end processHeads: ' + self._CLASSNAME)
        if not self.content_type:
            self.content_type = DEFAULT_CONTENT_TYPE
        Log.debug('content: ', self.content_type)
        Log.debug('end processHeads: ' + self._CLASSNAME)
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
    
    # @return:运行测试前需要执行的测试
    def getInitSetupFixture(self, rowpos):
        result = []
        fixtureName = ''
        fixtureParams = ''
        returnparam = ''
        for col in range(0, 2):
            temp = self.excelAPP.getCellStrValue(rowpos, col)
            if len(temp) > 1 and temp.lower().find('fixture') > -1:
                fixtureName   = self.excelAPP.getCellStrValue(rowpos, col)
                fixtureParams = self.excelAPP.getCellStrValue(rowpos, col + 1)
                returnparam   =  self.excelAPP.getCellStrValue(rowpos, col + 2)
                rowpos += 1
                break
        if fixtureName:
            result = [fixtureName, fixtureParams, returnparam]
        return result, rowpos
    
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
    
    #把保存上次请求的结果信息
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
                        self.preResultInfo[key] = self.getValueFromRespByDict(key, needSavePreResultDict[key], respDict)
                else:
                    print 'json or dictionary is error'  + self.needSavePreResults#忽略
            else:
                if not ('error' in respDict and respDict['error']):
                    needSavePreResultList = self.needSavePreResults.split(';')
                    for savePreResult in needSavePreResultList:
                        [key, value] = savePreResult.split('=')
                        self.preResultInfo[key] = self.getValueFromRespByPattern(value, resp)
        except BaseException, e:
            Log.error(e)
        Log.debug('end savePreResultInfo: ' + self._CLASSNAME)
        return self.preResultInfo
    
    def getValueFromRespByDict(self, key, respDict):
        keyvalue = ''
        if isinstance(respDict, dict) and key in respDict:
            keyvalue = str(respDict[key])
        return keyvalue
    
    def getValueFromRespByPattern(self, pattern, resp):
        result = ''
        temp = re.findall(pattern, resp, re.IGNORECASE)
        if temp:
            #获取匹配的第一个元组
            try:
                result = temp[0].split(":")[-1]#
            except BaseException, e:
                Log.error('getValueFromRespByPattern: ', e)
        return result
    
    
    def addPreResultToParams(self):
        self.addSpeficPreResultToParams()
         
    def setLoginInfo(self, client):
        Log.debug('start setLoginInfo: ' + self._CLASSNAME)
        if hasattr(self, 'initInfoBeforeTest') and self.initInfoBeforeTest:
            if "cookie" in self.initInfoBeforeTest:
                client.cookie = self.initInfoBeforeTest['cookie']
            if "token" in self.initInfoBeforeTest:
                client.token = self.initInfoBeforeTest['token']
            Log.debug("initInfoBeforeTest: ", self.initInfoBeforeTest)
        Log.debug('end setLoginInfo: ' + self._CLASSNAME)
    
    def addSpeficPreResultToParams(self):
        if hasattr(self, 'preResultInfo') and self.preResultInfo is dict:
            self.reqargs.update(self.preResultInfo)
    
    def setUrl(self):
        #如果测试用例没有url列,或者为空，则用表头的url值
        if not hasattr(self, 'url') or not self.url:
            if self.interface and self.function:
                self.url = self.interface + self.function
            else:
                Log.debug("self.interface or  self.function is none")
                Log.debug("self.url", self.url)
        return self.url
    
    def setRequestMethod(self):
        if not hasattr(self, 'requestMethod') and not self.requestMethod:
            self.requestMethod = 'post'
    
    #从测试文件，如excel或许excel中获取fixturename 列，并调用其run(),
    #@return result type, dict    
    def execFixture(self):
        if hasattr(self, 'userdefinefixture'):
            userdefinefixture = self.getFixture(self.userdefinefixture)
            self.userdefinefixtureresult = userdefinefixture.run()
    
    def getFixture(self, fixturePath):
        fixture = None
        temp = fixturePath.split('.')
        _CLASSNAME = temp[-1]
        if len(temp) == 1:
            fixturePath = 'fixture.' + _CLASSNAME
        try:
            exec 'import ' + fixturePath
            exec 'fixture = ' + fixturePath + '.' + _CLASSNAME + '()' 
        except BaseException, e:
            Log.error('getFixture error:', e)
        return fixture
    
    def runInitSetupFixture(self):
        Log.debug('start runInitSetupFixture: ' + self._CLASSNAME)
        fixturePath   = self.initSetupFixture[0]
        fixtureParams = self.initSetupFixture[1]
        returnparam   = self.initSetupFixture[2]
        fixture = self.getFixture(fixturePath)
        if fixture:
            self.initInfoBeforeTest = fixture.run(fixtureParams, returnparam)
            Log.debug('end runInitSetupFixture: ', self.initInfoBeforeTest)
        Log.debug('end runInitSetupFixture: ' + self._CLASSNAME)
                
    def genResultLink(self, respData):
        try:
            jsonResult = strToDict(respData)
            if jsonResult and 'data' in jsonResult:
                divName = 'div' + self.testCaseId
                self.link =  "<p align='left' ><br><a href=javascript:show('" + divName + "');>show json text</a></p>"  + \
                                "<br><div id='" + divName + "' style='display:none;'>"+ respData + "</div>"
            else:
                self.link = "<i>the Data of Response is %s<i>" %  respData
        except BaseException, e:
            print e
            self.link = " response data is %s " %  respData
                
    def saveRespDataToFile(self, respData):
        fileName = str(self.testCaseId + 'json.txt')
        path = LOGFIELPATH + self.curShName
        if not os.path.exists(LOGFIELPATH):
            os.mkdir(LOGFIELPATH)
        try:
            if not os.path.exists(path):
                os.mkdir(path)
            fileObject = open(path + os.sep + fileName, 'w')
            fileObject.write(respData)
            fileObject.close()
        except BaseException, e:
            Log.error("create jsontxt fail!", e)
            
    #若果请求的路径参数包含{变量}的变量，则从当期的测试参数中取
    #foxexample: url= http://www.xxx.com:8080/path1/{patah2}/p
    def setDynamicUrlPath(self, fromparams={}):
        Log.debug('start setDynamicUrlPath: ' + self._CLASSNAME)
        pattern = '{\\w+}'
        if not fromparams:
            fromparams = self.reqargs
        dynamicPathList = re.findall(pattern, self.url, re.IGNORECASE)
        try:
            for dynamicpath in dynamicPathList:
                dynamicpathVar = dynamicpath[1:-1] #去掉{}
                print fromparams
                if dynamicpathVar in fromparams:
                    self.url = self.url.replace(dynamicpath, fromparams[dynamicpathVar])
                else:
                    Log.error('setDynamicUrlPath fail, reqargs has not ' + dynamicpathVar)
        except Exception, e:
            Log.error(e)
        Log.debug('end setDynamicUrlPath: ' + self._CLASSNAME)
    
    #需要重新编写,去掉不做请求的参数
    def fliterParamlist(self):
        Log.debug('start fliterParamlist: ' + self._CLASSNAME)
        paramList = []
        for param in self._typeDict:
            #如果包含_下划线，表明不是用作请求参数
            if param.find('_') >0 or param.lower().find('url') > -1 \
                or param.lower().find('savepre') > -1 or \
                param.lower().find('fixture') > -1:
                continue
            paramList.append(param)
        return paramList
        Log.debug('end fliterParamlist: ' + self._CLASSNAME)

    def setReqParams(self):
        if hasattr(self, '_args'): #如果有_args变量
            self.setReqParamsByArgjson()
        else:
            self.setReqParamsByBuildinVar()
        
    def setReqParamsByBuildinVar(self):
        argv = self.fliterParamlist()
        if isinstance(argv, list):
            for arg in argv:
                self._addValueToParam(arg)
    
    def setReqParamsByArgjson(self):
        self.reqargs = strToDict(self._args)
        if self.reqargs:
            #如果json中包含%varname%的变量
            fromWhDict = strToDict(self.previousResp)
            if fromWhDict:
                for reqarg in self.reqargs:
                    value = self.reqargs[reqarg]
                    if value.find('%') > -1:
                        self.reqargs[reqarg] = \
                            self.getDynamicParamVlaue(value, fromWhDict)
        else:
            print 'setReqParamsByArgjson error', self._args
            print 'maybe the json format is wrong!'
            Log.error('setReqParamsByArgjson error', self._args)
      
    def getDynamicParamVlaue(self, paramvalue, fromWhDict):
        pattern = '%\\w+%' #动态参数
        result  = paramvalue
        try:
            valueList = re.findall(pattern, paramvalue, re.IGNORECASE)
            if len(valueList) > 0:
                keyvalue = valueList[0][1:-1] #去掉%%
                result = self.getValueFromRespByDict(keyvalue, fromWhDict)
                print keyvalue, result
        except BaseException, e:
            Log.error('getDynamicParamVlaue error:', e)
        return result
                    
    def _addValueToParam(self, arg):
        isnull = False
        if hasattr(self, arg):
            # self.arg的内容不为空
            exec "isnull = (self." + arg + " != '')"
            if isnull:
                exec 'temp = self.' + arg
                self.reqargs[arg] = temp

    def processData(self, data):
        return  ''
    
    def clearBeforeTest(self):
        if self.reqargs and isinstance(self.reqargs, dict):
            self.reqargs.clear()
    
    def befortest(self):
        Log.debug('start befortest: ' + self._CLASSNAME)
        self.setLoginInfo(self.client)
        Log.debug('end befortest: ' + self._CLASSNAME)

if __name__ == "__main__":
    print 'dff'
    import fixture.LoginFixture
    