# -*- coding: UTF-8 -*-
'''
@author: water
'''
from apifixture.HttpApiFixture import HttpApiFixture
from log.Log import Log
from util.jsonutil import strToDict

class MultipleHttpFixture(HttpApiFixture):
    '''
            用于测试基于http restful,http协议接口的多个接口，多个请求的测试构件
    '''

    _CLASSNAME = 'apifixture.MultipleHttpFixture'

    # test method, ruturn actual test result 
    # @return {} json, response data
    def test(self):
        Log.debug('start test: ' + self._CLASSNAME)
        self.clearBeforeTest()
        self.befortest()
        self.setReqParams()
        self.fixtureExecResult = self.execFixture() 
        #self.addPreResultToParams() #从上次请求产生的response中取得需要保存的参数信息，并保存到本次请求的参数列表中
        try:
            Log.debug('testCaseId:', self.testCaseId)
            self.setRequestMethod()
            #若果请求的路径信息中含有动态变量，则从参数列表中读取
            self.setDynamicUrlPath(self.reqargs)
            reqargs = self.fileUpload() #如果参数中包含filepath，则为文件上传
            respData = self.doRequest(self.url, reqargs, self.requestMethod)
            self.saveRespDataToFile(respData)
            self.genResultLink(respData)
        except BaseException, e:
            Log.error( e )
        Log.debug('end test: ' + self._CLASSNAME)
        return respData
    
    def fileUpload(self):
        reqargs = self.reqargs
        if 'filepath' in self.reqargs:
            self.requestMethod = 'upload'
            filepath = self.reqargs['filepath']
            Log.debug("filepath:", filepath.decode('utf-8').encode('gb2312'))
            reqargs = filepath.decode('utf-8').encode('gb2312')
    #                     self.reqargs = filepath.decode('utf-8').encode('gb2312')
            self.client.referer = "http://pre.moojnn.com/datasource.html" 
        return reqargs
    
        