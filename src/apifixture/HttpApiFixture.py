# -*- coding: UTF-8 -*-
# package: fixture.HttpApiFixture
'''
@author: Water.Zhang
'''

from apifixture.httpconf import DEFAULT_CONTENT_TYPE
from fixture.CommonFixture import CommonFixture
from fixture.ExcelColumnFixture import ExcelColumnFixture
from log.Log import Log


class HttpApiFixture(ExcelColumnFixture, CommonFixture):

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
    loginInfo  = {}
    preResultInfo = {}
    
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
        self.loginInfo, rowpos = self.getLoginInfo(rowpos, ncols)
        Log.debug('getLoginInfo rowpos:', rowpos)
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
    def getLoginInfo(self, rowpos, ncols):
        loginMsg = ''
        loginInfo = ''
        for col in range(0, ncols):
            loginMsg = self.excelAPP.getCellStrValue(rowpos, col)
            if len(loginMsg) > 1 and loginMsg.lower().find('loginfixture') > -1:
                loginFixtureName = self.excelAPP.getCellStrValue(rowpos, col)
                loginParams = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                loginfixturepath = "fixture." + loginFixtureName
                print loginfixturepath
                try:
                    exec 'import ' + loginfixturepath
                    # test class method
                    exec 'loginfixture = ' + loginfixturepath + '.' + loginFixtureName + '()' 
                    loginInfo = loginfixture.login(loginParams)
                except BaseException, e:
                    Log.error(e)
                    print e
                break
        Log.debug('loginInfo', loginInfo)
        return loginInfo, rowpos
    
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
    
        
