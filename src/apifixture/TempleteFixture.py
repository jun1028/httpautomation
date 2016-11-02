# -*- coding: UTF-8 -*-
# package: apifixture.TempleteFixture
'''
@author: water
'''

from apifixture import LOGFIELPATH
from apifixture.HttpApiFixture import HttpApiFixture
from check.result_check import ResultCheck
from httputil import HttpClientUtil
from log.Log import Log
from urllib2 import HTTPError
from util.jsonutil import strToDict
import os
import re

class TempleteFixture(HttpApiFixture):
    
    '''
            用于测试基于http restful,http协议接口的默认测试构件
    '''

    client = HttpClientUtil()
    clas = 'apifixture.TempleteFixture'
    jsonResult = {}
    strResult = ''
    link = ''
    fixtureExecResult = {}

    # test method, ruturn actual test result 
    # @return {} json, response data
    def test(self):
        Log.debug('start test: ' + self.clas)
        try:
            self.getUrl()
            #self.fixtureExecResult = self.getFixture()
            self.args = {}
            paramlist = self.getParamlist()
            self.addPreResultToParams()
            self.addParams(paramlist)
            Log.debug('testCaseId:', self.testCaseId)
            respData = ''
            try:
                #默认为post请求
                if not hasattr(self, 'requestMethod') and not self.requestMethod:
                    self.requestMethodself = 'post'
                if 'filepath' in self.args:
                    self.requestMethodself = 'upload'
                    filepath = self.args['filepath']
                    self.args = filepath
                self.setDynamicUrlPath()
                #开始HTTP请求
                resp = self.client.dorequest(self.url, self.args, \
                                             methodname=self.requestMethod)
                respData = resp.read()
                Log.debugvar('respData is ', respData)
            except HTTPError, e:
                respData = '{"error":"' + str(e) + '"}'
            except Exception, e:
                respData = '{"error":"' + str(e) + '"}'
            self.saveRespDataToFile(respData)
            self.genResultLink(respData)
        except BaseException, e:
            Log.error( e )
        Log.debug('end test: ' + self.clas)
        return respData

    def runTest(self, cell, a):
        Log.debug('start runTest: ' + self.clas)
        try:
            if not self.expected:
                self.expected = a.parse(cell.text)
        except BaseException, e:
            Log.debug("testcaseid " + str(self.testCaseId))  
            Log.debug(e)
            self.expected = ''
        try:
            actualresult = a.get()
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
        Log.debug('end runTest: ' + self.clas)
    
    def genResultLink(self, respData):
        try:
            self.jsonResult = strToDict(respData)
            if self.jsonResult and 'data' in self.jsonResult:
                if len(self.jsonResult['data']) > 0:
                    divName = 'div' + self.testCaseId
                    self.link =  "<p align='left' ><br><a href=javascript:show('" + divName + "');>show json text</a></p>"  + \
                                    "<br><div id='" + divName + "' style='display:none;'>"+ respData + "</div>"
            else:
                self.link = "<i>the Data of Response is %s<i>" %  respData
        except:
            self.link = "response data is %s " %  respData
                
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
            
    def compActualAndExpect(self, acutal, expect):
        bcompresult = True
        message   = ''
        return (bcompresult, message)
        
    #若果请求的路径参数包含{变量}的变量，则从当期的测试参数中取
    #foxexample: url= http://www.xxx.com:8080/path1/{patah2}/p
    def setDynamicUrlPath(self):
        Log.debug('start setDynamicUrlPath: ' + self.clas)
        pattern = '{\\w+}'
        dynamicPathList = re.findall(pattern, self.url, re.IGNORECASE)
        try:
            for dynamicpath in dynamicPathList:
                dynamicpathVar = dynamicpath[1:-1] #去掉{}
                if dynamicpathVar in self.args:
                    self.url = self.url.replace(dynamicpath, self.args[dynamicpathVar])
                    self.args.pop(dynamicpathVar)
                else:
                    Log.error('setDynamicUrlPath fail, args has not ' + dynamicpathVar)
        except Exception, e:
            Log.error(e)
        Log.debug('end setDynamicUrlPath: ' + self.clas)

    def getParamlist(self):
        Log.debug('start getParamlist: ' + self.clas)
        paramList = []
        for param in self._typeDict:
            if param.lower().find('test') > -1:
                continue
            paramList.append(param)
        return paramList
        Log.debug('end getParamlist: ' + self.clas)

    def addParams(self, argv):
        if isinstance(argv, list):
            for arg in argv:
                self._addParamToList(arg)

    def _addParamToList(self, arg):
        isnull = False
        if hasattr(self, arg):
            # self.arg的内容不为空
            exec "isnull = (self." + arg + " != '')"
            if isnull:
                exec 'temp = self.' + arg
                self.args[arg] = temp

    def processData(self, data):
        return  ''
#     
