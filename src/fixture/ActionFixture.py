# -*- coding: UTF-8 -*-
# package: fixture.ActionFixture
'''
@author: Water.Zhang
'''
__version__ = '1.0'

import datetime
import json
import os
import string
import sys
import time
import traceback
import urllib
import urllib2

from fixture.Actions import Actions
from log.Log import Log
from runner import GlobalSetting
from util.Report import Report
import util.excel
from util.sendmail import sendmail


TESTFLAG = False
NEEDCHECKISTESTSHEET = False



class ActionFixture(Report):
    """
    1.解析基于step的测试用例
    2.生成HTML测试报告
    """
    _CLASSNAME        = 'ActionFixture'
    # 用于标记excel文件中测试步骤开始的位置的标示 当读到excel中的cell 中含有step字符串时候，即开始执行测试
    _STARTSTEP        = 'step' 
    
    
    def __init__(self, isMakeReporterFlag=True):
        self.needSendmail = GlobalSetting.NEEDSENDMAIL

    #@param testcasepath:测试路径，为url或是一个excel文件名
    def runTests(self, testcasepath, reportFileName=''):
        Log.debug('start runTests: ' + self._CLASSNAME)
        self.summary["run date"] = time.ctime(time.time())
        self.summary["run elapsed time"] = RunTime()
        self.casenos = []
        if testcasepath.find('xls') > -1:
            self.getTestcasesByExcelFile(testcasepath)
        else:
            if testcasepath.find('http:') > -1:
                self.url = testcasepath
                case_no = self.url.split('=')[1]
            else:
                self.url = self.basetestcaseurl + 'case_no=%s' % testcasepath
                case_no = testcasepath
            self.casenos = self.getTestcasesByUrl(self.url, case_no)
        for testcase in self.casenos:
            self.counts = Counts()
            if self.testttpod and GlobalSetting.NEEDRESTARTTTPOD:
                #如果已经启动ttpod，则重新启动
                self.action.resetTtpod()
            #testcase type:tuple ,casename, steps[]
            self.case_no = testcase[0]
            self.setReportFileName(reportFileName, self.case_no)
            self.repstr = self.getReportHeader(self.case_no, needscrips=True)
            self.repstr += self.getReportTableHeader()
            if hasattr(self, 'title'):
                if self.title:
                    self.repstr += self.getReportTitle(self.title)
#             if hasattr(self, 'envinfo'):
#                 if self.envinfo:self.repstr += self.getReportEnvInfo(self.envinfo)
            self.repstr += self.getReportTableColumnName(self.reportTableColumnName)
            try:
                self.action.unlock()
                Log.debug('ok')
            except Exception, error:
                Log.error(type(error))
                Log.error(error)
                print 'unlock fail'
            #testcase , (testcsename, steps[])
            steps = testcase[1]
            if len(testcase) == 3:
                expecteds = testcase[2]
            else:
                expecteds = []
            try:
                self.runSteps(steps, expecteds)
                if self.action.crashflag:
                    break
            except KeyboardInterrupt:
                print 'exit test'
                sys.exit()
            #不需要动态fixture
#             fixturePath = self.getFixturePath()
#             if fixturePath == '':  # if have not fixture row, use default fixture
#                 self.runSteps(steps)
#             else:
#                 pass
            if self.isMakeReporterFlag:
                cpuChartLink = self.getCpuChartLink(self.reportFileName)
                self.repstr += self.getReportTail(self.counts.toString()\
                                                   + '<br>' + cpuChartLink)
                self.makeRepoter()
            if self.needSendmail:
                try:
                    subject = 'automation test report, sent automatically by system.....'
                    text = MESSAGETXT % self.counts.toString()
                    sendmail(subject, text, attachment1=self.reportFileName, \
                        attachment2=self.cpuRatioChartMap[self.reportFileName],\
                        receiver=self.mailaddr)
                except Exception, error:
                    print error
                    Log.error('send mail error')
                    Log.error(error)
            #清理之前的测试数据
            self._clear()
        self.makeSummaryReport()
        Log.debug('end runTests: ' + self._CLASSNAME)

    def runSteps(self, steps, expecteds=[]):
        Log.debug('start:runSteps' + self._CLASSNAME)
        if GlobalSetting.ISMONITORCPU:
            self.startCpuThread()
        if GlobalSetting.ISMONITORMEM:
            self.startMemThread()
        startCaseTime = datetime.datetime.now()
        self.action.automationtime = 0
        Log.debug('startCaseTime' + str(startCaseTime))
        for i in range(len(steps)):
            try:
                self.actionStartTime = time.time()
                preautomationtime = self.action.automationtime
                startsteptime = datetime.datetime.now()
                try:
                    self.testcaseid = str(i + 1)
                    expected = ''
                    if expecteds:
                        try:
                            expected = expecteds[i]
                        except Exception, err:
                            Log.error(err)
                    rowdata = self.doStep(steps[i], expected)
                    if self.action.crashflag:
                        break
                except (IndexError, KeyError), error:
                    Log.error(error)
                    break
                endsteptime = datetime.datetime.now()
                self.steptime = (endsteptime - startsteptime).total_seconds() -\
                                 self.action.automationtime + preautomationtime
                #print self.steptime
    #             Log.debug( 'step all time', (endsteptime - startsteptime).total_seconds() , \
    #                     preautomationtime, 'step',steps[i][str(i+1)], self.steptime )
                self.repstr += self.getReportTableRow(rowdata)
            except KeyboardInterrupt:
                sys.exit(0)
        endCaseTime = datetime.datetime.now()
        testCaseTime = (endCaseTime - startCaseTime).total_seconds()
        duration = testCaseTime - self.action.automationtime
        Log.debug('DURATION' + str(duration) + \
                  str(testCaseTime) + str(self.action.automationtime))
        #print duration
        self.passTestResultToSer(testCaseTime)
        self.saveCounts()
        if GlobalSetting.ISMONITORCPU:
            self.endCputhread()
        if GlobalSetting.ISMONITORMEM:
            self.endMemthread()
        Log.debug('end runSteps: ' + self._CLASSNAME)

    def getFixturePath(self, rowpos, ncols=5):
        fixturePath = ''
        for col in range(0, ncols):
            temp = self.excelAPP.getCellStrValue(rowpos, col)
            if len(temp) > 1:
                if temp.find("fixture") > -1:  # $ means fixture row
                    fixturePath = temp
                    rowpos += 1
                break
        return fixturePath, rowpos

    def getenvinfo(self, rowpos, col=0):
        envinfo = self.excelAPP.getCellStrValue(rowpos, col)
        col += 1
        if envinfo.find('enviroment info') > -1:
            rowpos += 1
            self.envinfo['type'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['resoultion'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['androidversion'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['appversion'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['testnetwork'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['testsong'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            self.envinfo['detilinfo'] = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
        return rowpos

    def getStartStep(self, rowpos, col=0):
        while True:
            step = self.excelAPP.getCellStrValue(rowpos, col)
            rowpos += 1
            if step.find(self._STARTSTEP) > -1: #获取test step的位置
                break
            if rowpos > 10:
                print self.cursheet, ' no test step ,error !'
                rowpos = -1
                break
        return rowpos

    def getTitle(self, rowpos, ncols=5):
        title = ''
        for col in range(0, ncols):
            tl = self.excelAPP.getCellStrValue(rowpos, col)
            if len(tl) > 1:
                title = str(tl)
                title = title.replace('TestCases', 'test')
                title = title.replace('Test Cases', 'test')
                title = title + ' Report'
                title = title.title()
                rowpos += 1
                break
        return title, rowpos

    def getTestcasesByUrl(self, url, case_no, MutiTestCaseFlag=False):
        Log.debug('start getTestcasesByUrl: ' + self._CLASSNAME)
        self.url = url
        if not MutiTestCaseFlag:#如果不是多个测试用例
            if not TESTFLAG:
                casenames = GlobalSetting.TESTCASENOS
                for case_no in casenames:
                    if self.url:
                        try:
                            caseurl = self.url.split('=')[0] 
                        except IndexError, e:
                            print 'test case url is error'
                            Log.error(e)
                        #tuple ,casename, steps[]
                        testcase = [case_no, \
                            self.getSteps(''.join([caseurl, '=', case_no]))]
                        self.casenos.append(testcase)
                    else:
                        break
            else:
                testcase = [case_no, self.getSteps(self.url)]
                self.casenos.append(testcase)
        else:
            self.casenos = self.getCasenos(case_no)
        Log.debug('end getTestcasesByUrl: ' + self._CLASSNAME)
        return self.casenos

    def checkIsTestSheet(self, sheets):
        testsheets = []
        for sheetName in sheets:
            if sheetName.lower().find("test") > 0:
                testsheets.append(sheetName)
        return testsheets

    def getTestcasesByExcelFile(self, excelfilename):
        Log.debug('start: getTestcasesByExcelFile' + self._CLASSNAME)
        self.excelAPP = util.excel.ExcelAppRD()
        self.excelAPP.openExcel(excelfilename)
        sheets = self.excelAPP.getShNameList()
        if NEEDCHECKISTESTSHEET:
            testsheets = self.checkIsTestSheet(sheets)
        else:
            testsheets = sheets
        if len(testsheets) == 0:
            print u'在EXCEL文件中没有包含_test名称的sheet，若需要测试某个sheet此sheet的名称需要加上"_test"'
            print 'exit'
            sys.exit()
        for sheetName in testsheets:
            steps = []
            expecteds = []
            self.curShName = sheetName
            self.case_no = self.curShName
            sheet = self.excelAPP.getShByName(sheetName)
            self.cursheet = sheet
            nrows = sheet.nrows
            ncols = sheet.ncols
            if nrows < 2 or ncols < 2:
                continue
            rowpos = 0
            self.title, rowpos = self.getTitle(rowpos)
            rowpos = self.getenvinfo(rowpos)
            startrow = self.getStartStep(rowpos)
            if rowpos == -1:
                continue
            row = startrow
            while row < nrows:
                #the second column is step
                step = self.excelAPP.getCellStrValue(row, 1)
                steps.append(step)
                #the third column is step
                expected = ''
                try:
                    if ncols > 2:
                        expected = self.excelAPP.getCellStrValue(row, 2)
                except Exception, err:
                    Log.error(err)
                expecteds.append(expected)
                row += 1
            self.casenos.append((self.case_no, steps, expecteds))
        Log.debug('end: getTestcasesByExcelFile' + self._CLASSNAME)
        return self.casenos

    def setReportFileName(self, reportFileName, casename=''):
        if not os.path.exists(self._DEFAULTREPORTER):
            os.mkdir(self._DEFAULTREPORTER)
        if reportFileName and reportFileName.find('.html') > -1:
            reportFileName = reportFileName[:-5]
        else:
            reportFileName = casename
        self.reportFileName = self._DEFAULTREPORTER + reportFileName \
                                + '_' + str(self.iterationCount) + '.html'

    def _clear(self):
        del self.counts

    def saveCounts(self):
        if self.reportFileName:
            self.summaryCounts[self.reportFileName] = self.counts 
#         self.counts = Counts()

    def startMemThread(self):
        Log.debug('start startMemThread: ' + self._CLASSNAME)
        try:
            if GlobalSetting.ISMONITORMEM \
                and self.case_no.find('install') < 0:
                memReportName = self.case_no + '_' + str(self.iterationCount)\
                                             + '_mem.html'
                filedir = DEFAULTMEMLINECHART
                if not os.path.exists(filedir):
                    os.mkdir(filedir)
                memChartPath = filedir + self.case_no + str(self.iterationCount) + '.png'
#                 self.memRatioChartMap[self.reportFileName] = memChartPath
                self.memthread = MemThread(serialno     = self.action.serialno, \
                                           reportname   = memReportName, \
                                           memChartPath = memChartPath)
                #主线程结束后，影子线程
                Log.debug('start mem thread')
                self.memthread.start()
        except Exception, e:
            Log.error(e)
        Log.debug('end startMemThread: ' + self._CLASSNAME)

    def endMemthread(self):
        Log.debug('start endMemthread: ' + self._CLASSNAME)
        try:
            self.memthread.endFlag = True
            self.memthread.join(60)
        except Exception, e:
            Log.error(type(e))
            Log.error(e)
            self.memthread.exit()
        Log.debug('end endMemthread: ' + self._CLASSNAME)

    def startCpuThread(self):
        Log.debug('start startCpuThread: ' + self._CLASSNAME)
        try:
            if self.case_no.find('install') < 0:
                cpuReportName = self.case_no + '_' + str(self.iterationCount)\
                                             + '_cpu.html'
                filedir = DEFAULTCPULINECHART
                if not os.path.exists(filedir):
                    os.mkdir(filedir)
                cpuChartPath = filedir + self.case_no + str(self.iterationCount) + '.png'
                self.cpuRatioChartMap[self.reportFileName] = cpuChartPath
                self.cputhread = CpuThread(serialno     = self.action.serialno, \
                                           reportname   = cpuReportName, \
                                           cpuChartPath = cpuChartPath)
                #主线程结束后，影子线程
                #self.cputhread.setDaemon(True)
                Log.debug('start cpu thread')
                self.cputhread.start()
        except Exception, e:
            Log.error(e)
        Log.debug('end startCpuThread: ' + self._CLASSNAME)

    def endCputhread(self):
        Log.debug('start endCputhread: ' + self._CLASSNAME)
        try:
            self.cputhread.endFlag = True
            #等待cpuThread结束
            self.cputhread.join(60)
        except Exception, e:
            Log.error(type(e))
            Log.error(e)
            self.cputhread.exit()
        Log.debug('end endCputhread: ' + self._CLASSNAME)

    def floatToPercentage(self, floatDatas):
        pass

    def doStep(self, step, expected=''):
        Log.debug('start doStep: ' + self._CLASSNAME)
        if GlobalSetting.ISMONITORCPU:
            self.cputhread.curStep = step
        if GlobalSetting.ISMONITORMEM:
            self.memthread.curStep = step
        self.curstep = step
        cell = self.getCell(step)
        actionstr, arg1, arg2 = self.action.parseAction(step)
        if expected:
            arg2 = expected
        try:
            self.action.actionstep[self.testcaseid] = [actionstr, arg1]
        except Exception, err:
            Log.error(err)
            Log.error('self.actionstep[self.testcaseid] ')
        Log.debugvar('expected: ', expected)
        #Log.debugvar(actionstr, arg1)
        if actionstr != '':
            #检查TTPOD是否crash
            if NEEDCHECKCRASH:
                try:
                    if self.testttpod and self.case_no.find('install') < 0:
                        self.action.curstep = self.curstep
                        iscrash, crashlog = self.action.isTtpodCrash()
                        if iscrash:
                            self.action.logTtpodCrash(actionstr, crashlog)
                            self.action.crashflag = True
                            return
                            #self.action.resetTtpod()
                except Exception, err:
                    Log.error(err)
                    Log.error("check ttpod crash error!")
            if 'result' in self.action.resultinfo:
                self.action.resultinfo['result'] = ''
            self.actionTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                self.action.method(actionstr, arg1, arg2)
            except KeyboardInterrupt:
                sys.exit()
            except RuntimeError, error:
                Log.error(error)
                util.AdbCmd.restartServer()
                if util.AdbCmd.getDeviceCount() == 0:
                    if hasattr(self.action, 'currentDeviceIp'):
                        self.action.connToDeviceByIp(self.action.currentDeviceIp)
                    else:
                        self.action.connByDefaultIpaddr()
        else:
            print 'the action string is null'
            print 'test case step format is error'
            print 'please check test case sheet'
            print 'the first line is test case id'
            print 'the second line is test step'
            Log.error(step)
            Log.error('action string is null')
            return
        if cell.text == '' or cell.text == ' ':
            cell.text = '&nbsp;'  # space
        rowdata = self.genData(step, expected)
        Log.debug('end doStep: ' + self._CLASSNAME)
        return cell.__str__() + rowdata

    #return tuple [{}]
    def getSteps(self, url):
        steps = []
        try:
            resp = urllib2.urlopen(url).read()
            jsondata = json.loads(resp, encoding="UTF-8")
            data = jsondata['data']
            #print data
            for i in range(0, len(data)):
                #data format,"data":[{"1":"\u542f\u52a8","2":"ddfdf"}
                #data中的第i个key的value
                steps.append(data[i][str(i + 1)])
        except urllib2.HTTPError, error:
            print "ERROR: ", error.read()
        return steps

    def getCasenos(self, url):
        print 'does not implement!'
        return []

    def makeRepoter(self):
        Log.debug('start makeRepoter: ' + self._CLASSNAME)
        try:
            try:
                self.outputReport = open(self.reportFileName, 'w')
                self.outputReport.write(self.repstr)
                self.outputReport.flush()
                self.outputReport.close()
                self.reportNameList.append(self.reportFileName)
            except IOError, e:
                Log.error(e)
#             Log.error('reportFileName does not exists ' + self.reportFileName)
        finally:
            self.outputReport.close() 
        Log.debug('end makeRepoter: ' + self._CLASSNAME)

    def makeSummaryReport(self):
        Log.debug('start makeSummaryReport: ' + self._CLASSNAME)
        if hasattr(self, 'reportNameList') and len(self.reportNameList) > 1:
            if not os.path.exists(self._DEFAULTREPORTER):
                os.mkdir(self._DEFAULTREPORTER)
            self.summaryReport = open(self._DEFAULTREPORTER + 'summary.html', 'w')
            self.repstr = self.getReportHeader('summary report')
            self.repstr += self.getReportTableHeader()
            columnNames = ['name', 'summary result', 'detail reporter url']
            if self.ismonitorcpu:
                columnNames.append('ttpod cpu utilization')
            self.repstr += self.getReportTableColumnName(columnNames)
            for reportName in self.reportNameList:
                try:
                    counts = self.summaryCounts[reportName]
                except:
                    counts = 'ERROR:NO DATA'
                countcell = Cell(counts)
                if hasattr(counts, 'wrong') and counts.wrong > 0:
                    countcell.addToTag(" bgcolor=\"#ffcfcf\"")
                else:
                    #green
                    countcell.addToTag(" bgcolor=\"#cfffcf\"")
                name = reportName.split(os.sep)[1]
                linkcell = Cell('<a href=%s>link to html</a>' % name)
                try:
                    filename = name[:-12]
                except:
                    filename = 'filename'
                namecell = Cell(filename)
                rowdata = namecell.__str__() \
                            + countcell.__str__() \
                            + linkcell.__str__()
#                 if self.ismonitorcpu:
#                     self.cpuChart = Cell('<a href=..\\%s>open cpu chart</a>' \
#                                      %self.cpuRatioChartMap[reportName])
                rowdata += Cell(self.getCpuChartLink(reportName)).__str__()
                self.repstr += self.getReportTableRow(rowdata)
            self.repstr += self.getReportTail()
            self.summaryReport.write(self.repstr) 
            self.summaryReport.flush()
            self.summaryReport.close() 
            print 'make summary report ok'
        Log.debug('end makeSummaryReport: ' + self._CLASSNAME) 

    def getCpuChartLink(self, reportName):
        if self.ismonitorcpu:
            self.cpuChart = '<a href=..\\%s>openExcel cpu chart</a>' \
                             % self.cpuRatioChartMap[reportName]
            return self.cpuChart
        else:
            return ''

    def getCell(self, text):
        return Cell(text)

    def genData(self, step, expected=''):
        Log.debug('start genData: ' + self._CLASSNAME)
        resultcell = Cell('')
        if 'result' in self.action.resultinfo:
            result = self.action.resultinfo['result']
            if result.find('ok') == 0 \
                or result.find('pass') == 0\
                or result.find('success') > -1:
                print 'testcaseid is ', self.testcaseid
                print self.curstep, 'test ok'
                self.right(resultcell, result)
                status = 1 # pass
            elif result.find('fail') > -1:
                print self.curstep, 'test fail'
                self.wrong(resultcell, result)
                status = 0 # fail
            else:
                self.output(resultcell, result)
                status = 2 # default
            #存测试步骤的结果信息到Server
            self.passTestStepResultToSer(status)
        cpucell = Cell('')
        if self.ismonitorcpu:
            self.outputcpudata(cpucell)
        if 'expectresult' in self.action.resultinfo \
            and self.action.resultinfo['expectresult']:
            expectedcell = Cell(expected)
            if self.action.resultinfo['expectresult'].find('ok') > -1 or \
                self.action.resultinfo['expectresult'].find('pass') > -1:
                self.right(expectedcell, self.action.resultinfo['expectresult'])
            else:
                self.wrong(expectedcell, self.action.resultinfo['expectresult'])
        else:
            expectedcell = Cell(expected)
        rowdata = resultcell.__str__() \
                        + expectedcell.__str__() \
                        + cpucell.__str__() \
                        + Cell(self.actionTime).__str__()
        Log.debug('end genData: ' + self._CLASSNAME)
        return rowdata

    def setEnvInfo(self, rowpos, col=0):
        self.envinfo['type'] = ''
        self.envinfo['resoultion'] = ''
        self.envinfo['androidversion'] = ''
        self.envinfo['appversion'] = ''
        self.envinfo['testnetwork'] = ''
        self.envinfo['testsong'] = ''
        self.envinfo['detilinfo'] = ''

    def strip(self, name):
        result = ''
        try:
            name = name.replace(' ', '')
            result = name.replace('\n', '') 
        except:
            pass
        return result

    def getTargetClass(self):
        return self.__class__

    # public static void right (Parse cell) {
    def right(self, cell, actual=None):
        cell.addToTag(" bgcolor=\"#cfffcf\"") # green
        self.counts.right += 1
        if actual != None:
            cell.addToBody(self.escape(actual))

    # public static void output (Parse cell) {
    def output(self, cell, actual=None):
        cell.addToTag(" bgcolor=gray")
        self.counts.right += 1
        cell.overrideToBody(actual)

    def getMaxCpuvalue(self, data=[]):
        maxcpu = 0
        for cpudata in data:
            if cpudata > maxcpu:
                maxcpu = cpudata
        return maxcpu

    # public static void output (Parse cell) {
    def outputcpudata(self, cell):
        try:
            highestcpuvalue = self.cputhread.highestcpuvalue[self.curstep]
            if highestcpuvalue:
                cell.overrideToBody(str(highestcpuvalue))
            if self.getMaxCpuvalue(highestcpuvalue) > OVERTOPCPULINE:
                cell.addToTag(" bgcolor=\"#ffcfcf\"")
            else:
                cell.addToTag(" bgcolor=\"#cfffcf\"")
        except Exception, error:
#             print 'get highest cpu value error'
            Log.error(error)
            Log.error(self._CLASSNAME + ":outputcpudata error" )
#         if self.cputhread.cpuDataDict.has_key(self.cputhread.curStep):
#             #cell.overrideToBody(self.cputhread.cpuDataDict[self.cputhread.curStep][0])
#             cell.overrideToBody(self.cputhread.cpuDataDict['highestcpuvalue'])
#         else:
#             Log.error('cpu thread error, the key: ' + self.cputhread.curStep + ' does not exist!')

    # public static void wrong (Parse cell) {
    # public static void wrong (Parse cell, String actual) {
    def wrong(self, cell, actual=None):
        cell.addToTag(" bgcolor=\"#ffcfcf\"")
        self.counts.wrong += 1
        if actual != None:
            cell.addToBody("<font size=2.0pt>%s</font>" % actual)
        if 'failimage' in self.action.resultinfo:
            Log.debug(unicode(self.action.resultinfo['failimage'], "gb2312"))
            cell.addToBody("<hr><font size=2.0pt><a href=..\\%s>fail image link</a></font>"\
                            % unicode(self.action.resultinfo['failimage'], "gb2312")) #unicode(pagename, "gb2312")   

    # public static void exception (Parse cell, Exception exception) {
    def exception(self, cell, exception):
        type, val, tb = sys.exc_info()
        err = string.join(traceback.format_exception(type, val, tb), '')
        cell.addToBody("<hr><pre><font size=-2>%s</font></pre>" % err)
        cell.addToTag(" bgcolor=\"#ffffcf\"")
        self.counts.exceptions += 1

    def _counts(self):
        return self.counts.toString()

    def label(self, string):
        return " <font size=-1 color=#c08080><i>%s</i></font>" % string

    def gray(self, string):
        return " <font color=#808080>%s</font>" % string

    def greenlabel(self, string):
        return " <font size=-1 color=#80c080><i>%s</i></font>" % string

    def escape(self, thestring, old=None, new=None):
        if old == None:
            return self.escape(self.escape(thestring, '&', "&amp;"), '<', "&lt;")
        else:
            return str(thestring).replace(old, new)

    #status, 0 means pass, 1 means fail, 2 only means output 
    def passTestStepResultToSer(self, status):
        '''
        pass test result to server
        '''
        Log.debug('start passTestStepResultToSer: ' + self._CLASSNAME) 
        try:
            if self.isPassDataToPhpFlag:
#                 print 'pass step test data to PHP'
                if GlobalSetting.ISMONITORCPU:
                    cpu = self.cputhread.cpuDataDict[self.cputhread.curStep]
                else:
                    cpu = 'no data'
                passResultToPhp(RESULTSTEPURL, {'case_no':self.case_no,\
                                                'step':self.curstep, \
                                                'status':status,
                                                'cpu':cpu,\
                                                'create_at':self.actionStartTime}) # test case number, step name, test result , cpu data
        except Exception, e:
            Log.error('can not write step data to PHP')
            Log.error(e)
        Log.debug('end passTestStepResultToSer: ' + self._CLASSNAME) 

    def passTestResultToSer(self, testCaseTime):
        Log.debug('start passTestResultToSer: ' + self._CLASSNAME) 
        try:
            if self.isPassDataToPhpFlag:
                duration = testCaseTime - self.action.automationtime
                print 'pass test result into php'
                vppver = self.getAppver()
                passResultToPhp(RESULTTESTURL,\
                                {'mobile_serial': self.action.serialno,\
                                'case_no': self.case_no, \
                                'app_version': vppver, \
                                'duration': duration, \
                                'failed_count': self.counts.wrong, \
                                'success_count': self.counts.right})
        except Exception, e:
            Log.error('can not write test data to PHP')
            Log.error(e)
        Log.debug('end passTestResultToSer: ' + self._CLASSNAME) 

    def getAppver(self):
        if hasattr(self, 'appver'):
            appver = self.appver
        else:
            appver = GlobalSetting.APPVERSION
        return appver


# from fixture.Fixture
class Counts:

    def __init__(self):
        self.right = 0
        self.wrong = 0
        self.ignores = 0
        self.exceptions = 0

    def clear(self):
        self.right = 0
        self.wrong = 0
        self.ignores = 0
        self.exceptions = 0

    def toString(self, testStep=True):
        if testStep:
            result = ("%s step test ok, %s step test fail, %s ignored, %s exceptions" % 
                (self.right, self.wrong, self.ignores, self.exceptions))
        return result

    def tally(self, source):
        self.right += source.right
        self.wrong += source.wrong
        self.ignores += source.ignores
        self.exceptions += source.exceptions

    def __str__(self):
        return self.toString()


# from fit.Fixture
class RunTime:
    def __init__(self):
        self.start = time.time()
        self.elapsed = 0.0

    def __str__(self):
        return self.toString()

    def toString(self):
        self.elapsed = time.time() - self.start
        if self.elapsed > 600:
            hours = self.d(3600)
            minutes = self.d(60)
            seconds = self.d(1)
            return "%s:%02s:%02s" % (hours, minutes, seconds)
        else:
            minutes = self.d(60)
            seconds = self.d(1)
            hundredths = self.d(.01)
            return "%s:%02s.%02s" % (minutes, seconds, hundredths)

    def d(self, scale):
        report = int(self.elapsed / scale)
        self.elapsed -= report * scale
        return report


class Cell:

    text = ''
    tag = ''

    def __init__(self, text):
        self.text = text
        self.tag = '<td align=left>'

    def addToTag(self, text):
        self.tag = self.tag[:-1] + text + ">"

    def addToBody(self, text):
        self.text = self.text + text

    def overrideToBody(self, text):
        self.text = text

    # modify some tag's value by tag
    def modifyTagValue(self, tag, value):
        resultFlag = False
        tagTuple = self.tag.split(' ')
        oldTag = ''
        tag = tag.strip()
        for oldTag in tagTuple:
            if oldTag.find(tag) > -1:
                newTag = tag + '=' + str(value)
                if oldTag.find('>') > -1:
                    self.tag = self.tag.replace(oldTag, newTag + '>')
                else:
                    self.tag = self.tag.replace(oldTag, newTag)
                resultFlag = True
                break
        return resultFlag

    def __str__(self):
        s = self.tag
        s += str(self.text)
        s += '</td>'
        return s

if __name__ == '__main__' :
#     action = Actions()
#     action.connToDevice()
    ea = ActionFixture()
#     a1,a2,a3 =  ea.parseAction('启动ttpo等等d')
#     print  unicode(a2, "gb2312")
#     print ea.parseAction('检查网页')
#     print ea.parseAction('退出')
#     #ea.runTests('http://qa.ttpod.com/app/get_test_case?case_no=demon-test-01')
    ea.reportNameList = ['report'+ os.sep +'jun1.html','report\\jun2.html']
    ea.makeSummaryReport()
