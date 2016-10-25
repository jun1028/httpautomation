# encoding=utf-8
"""
    检查接口返回结果
"""
from util import strToDict
import re


__version__ = '0.0.1'


class ResultCheck(object):
    """
    class to check result:
    This class is used to check the results returned by the interface. Parameters must be dictionary type.
    """

    version = "ResultCheck/%s" % __version__

    def __init__(self):
        # pass
        pass

        # assert isinstance(self.dic, dict), 'para must be dict'
        # assert 'status' in self.dic, 'dict has not the key named status'
        # assert 'message' in self.dic, 'dict has not the key named message'

    @staticmethod
    # 检查接口出参是否与预期结果中的参数一致，包含参数名、参数数量
    def CmpOutPara(ActualResultDict, ExpectResultDict):
        # 检查http请求返回码，如果不是200不再检查参数。
        # HttpStatus,HttpStatusMessage = self.ReadStatus(ActualResultDict)
        # if not HttpStatus:
        #     return False, HttpStatusMessage
        KeyActualResultDict = ActualResultDict['response'].keys()
        KeyExpectResultDict = ExpectResultDict['response'].keys()
        # 检查参数是否一致
        if cmp(KeyActualResultDict, KeyExpectResultDict) != 0:
            if len(KeyExpectResultDict) > len(KeyActualResultDict):
                InterfaceParaMessage = '返回结果中缺少参数'
                return False, InterfaceParaMessage
            elif len(KeyExpectResultDict) < len(KeyActualResultDict):
                InterfaceParaMessage = '返回结果中多传了参数'
                return False, InterfaceParaMessage
            else:
                InterfaceParaMessage = '返回结果以下参数不正确:'
                for i in range(len(KeyExpectResultDict)):
                    if KeyExpectResultDict[i] not in KeyActualResultDict[i]:
                        InterfaceParaMessage += '、' + KeyExpectResultDict[i]
                return False, InterfaceParaMessage
        else:
            InterfaceParaMessage = '返回的参数正确'
            return True, InterfaceParaMessage

    # all模式，
    @staticmethod
    def AllOutValue(actualResult, ExpectResultDict):
        ActualResultDict = strToDict(actualResult)
        if cmp(str(ActualResultDict['response']), str(ExpectResultDict['response'])) == 0:
            InterfaceMessage = '接口返回的结果完全正确'
            InterfaceStatus = True
            return InterfaceStatus, InterfaceMessage
        else:
            InterfaceMessage = '接口返回的结果不完全正确'
            InterfaceStatus = False
            return InterfaceStatus, InterfaceMessage

    # part模式
    @staticmethod
    def partOutValue(actualResultDict, expectResultDict):
        bCmpResult = -1
        message = ""
        #resultCount = 0
        resp = expectResultDict['response']
        respDict = strToDict(resp)
        actualResultDict = strToDict(actualResultDict)
        for key, value in respDict.iteritems():
            if actualResultDict[key] == value:
                bCmpResult, message = 1, "test pass"
            else:
                bCmpResult, message = 0, "test fail" + "actual result: " \
                                         + actualResultDict[key] + "expect result: " + value
                break
        return (bCmpResult, message)
    
    @staticmethod
    def verfyStrResult(actualResultStr, expectResult):
        bCmpResult = -1
        message    = '' 
        matchResult = re.findall(expectResult, actualResultStr, re.IGNORECASE)
        if matchResult:
            bCmpResult = 1
            message    = matchResult
        else:
            bCmpResult = 0 
            message    = actualResultStr
        return bCmpResult, message
        
        
    @staticmethod
    def checkResult(actualResult, expectResult):
        bCmpResult, message = -1, "only output"
        if expectResult.find('{') > -1: #json
            expectResultDict = strToDict(expectResult)
            if "type" in expectResultDict and expectResultDict['type'] == 'part':
                print 'part'
                bCmpResult, message = ResultCheck.partOutValue(actualResult, expectResultDict)
            elif 'error' in expectResultDict and  expectResultDict['type'] == 'error':
                bCmpResult, message = 1, str(expectResultDict)
            else:
                bCmpResult, message = ResultCheck.verfyStrResult(actualResult, str(expectResultDict))
                #bCmpResult, message = self.PartOutValue(actualResult, expectResultDict)
        else: #正则
            bCmpResult, message = ResultCheck.verfyStrResult(actualResult, expectResult)
#         message = unicode(message, "gb2312")
        return bCmpResult, message


if __name__ == '__main__':

    a = {'status': 200, 'response': {'a': 2, 'messagee': {'c': 'asd'}, 'c': 'as'}}
    b = {'type': 'part', 'response': {'a': 2, 'c': 'asd'}}
    c = {'status': 200, 'message': 2, 'a': 2, 'messagee': 3}

    aaa = ResultCheck()
    (ResultStatus, ResultStatusMessage) = aaa.ReadStatus(a)

    if ResultStatus:
        # print aaa.CmpOutPara(a, b)
        (ResultStatus, ResultStatusMessage) = aaa.CheckResult(a, b)
        print ResultStatus, ResultStatusMessage


