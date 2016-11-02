# -*- coding: UTF-8 -*-
# package: fixture.ExcelColumnFixture
'''

@author: Water.Zhang
'''

import os
import string
import sys
import time
import traceback
import webbrowser

from fit.TypeAdapter import adapterOnField, adapterOnMethod
from log.Log import Log
from runner import GlobalSetting
from util.Report import Report


REPORTPATH = 'reports' + os.sep
FAILREPORTPATH = REPORTPATH + 'fail' + os.sep


class ExcelColumnFixture(Report):

    """
    1. read test case from excel file
    2. execute test by invoke specified method in excel file
        or default test method implemented by subclass
    3. make html report
    notes: sheet name of test case need include "test" string, otherwise will ignore it.
            the first row need specify fixture name,if not ,will use TempleteFixture
            the first column must be testCaseId
    """

    _typeDict = {}
    _CLASSNAME = 'fixture.ExcelColumnFixture'
    _DEFAULTREPORTER = 'reports' + os.sep
    summaryReportName = _DEFAULTREPORTER + 'summary.html'
    results = {}  # result of each test case
    testCaseIdRangeFlag = GlobalSetting.TESTCASEID_RANGE_FLAG
    testCaseIdStart     = GlobalSetting.TESTCASEID_START
    testCaseIdEnd       = GlobalSetting.TESTCASEID_END

    def __init__(self):
#         self.counts = Counts()
        self.summaryCounts = {}
        self.summary = {}
        self.results = {}
        self.title = ''
        self.fixturePath = ''
        self.columnBindings = []
        self.excelAPP = None
        self.reportFileName = ''
        self.curShName = ''
        self.posDict = {'methodPos': -1}
        self.colspan = 1
        self.rowspan = '1'
        self.isMakeReporterFlag = True
        self.startFlag = False
        self.endFlag  = False
        self.expected = ''

    def _clear(self):
        self.startFlag = False
        self.endFlag   = False
        del self.heads

    # @param input: excel APP object
    # @param output: test report
    def dosheets(self, excelAPP, reportFileName):
        Log.debug('start: ExcelColumnFixture.dosheets')
        self.excelAPP = excelAPP
        self.reportFileName = reportFileName
        self.summary["run date"] = time.ctime(time.time())
        self.summary["run elapsed time"] = RunTime()
        sheets = self.excelAPP.getShNameList()
        self.reportNameList = []
        try:
            if not os.path.exists(REPORTPATH):
                os.mkdir(REPORTPATH)
            if not os.path.exists(FAILREPORTPATH):
                os.mkdir(FAILREPORTPATH)
        except:
            Log.error("create report fail")
        for sheetName in sheets:
            self.counts = Counts()
            if sheetName.lower().find("test") == -1:
                continue
            self.resetReportFileName(reportFileName, sheetName)
            self.reportNameList.append(self.reportFileName)
            #self.reportNameList.append(self.failReportFileName)
            print 'start test: ', sheetName
            try:
                self.doSheet(excelAPP, sheetName)
            except KeyboardInterrupt:
                sys.exit(0)
        self.makeSummaryReport()
        Log.debug('end: ExcelColumnFixture.dosheets')

    def doSheet(self, excelAPP, sheetName):
        Log.debug('start: ExcelColumnFixture.doSheet')
        sheet = self.excelAPP.getShByName(sheetName)
        self.excelAPP.setSheet(sheet)
        ncols = sheet.ncols
        nrows = sheet.nrows
        try:
            fixturePath, rowpos = self.getFixturePath(0, ncols)
            if fixturePath == '':  # if have not fixture row, use default fixture
                print 'warning:'
                print 'no specify fixture path or fixture in the first row in excel'
                print 'automation will use default fixture, apifixture.TempleteFixture'
                Log.debug('automation use default fixture, apifixture.TempleteFixture')
                fixturePath = 'apifixture.TempleteFixture'
                #sys.exit(0)
                #fixturePath = 'apifixture.TempleteFixture'
            clas = fixturePath.split('.')[-1]
            i = fixturePath.split('$')
            if len(i) == 1:
                exec 'import ' + fixturePath
                # test class method
                exec 'fixture = ' + fixturePath + '.' + clas + '()' 
            else:
                exec "import %s" % (i[0],)
                exec "fixture = %s.%s()" % (i[0], i[1])
        except ImportError, e:
            Log.exception(e)
            print 'fixturePath does not exists'
            print 'system exit'
            return
        fixture.counts = self.counts  # dynamic variable
        fixture.summary = self.summary
        fixture.excelAPP = self.excelAPP
        fixture.fixturePath = self.fixturePath
        fixture.reportFileName = self.reportFileName
        fixture.failReportFileName = self.failReportFileName
        fixture.curShName = self.curShName
        fixture.reportNameList = self.reportNameList
        fixture.summaryCounts = self.summaryCounts
        fixture.doRows(rowpos, nrows, ncols)
        Log.debug('end: ExcelColumnFixture.doSheet')

    def doRows(self, rowpos, nrows, ncols):
        Log.debug('start: ExcelColumnFixture.doRows')
        self.title, rowpos = self.getTitle(rowpos, ncols)
        rowpos = self.processHeads(rowpos, ncols)
        #setup before test
        if hasattr(self, 'runSetupFixture'):
            self.runSetupFixture()
        self.repstr = self.getReportHeader(self.curShName, needscrips=True)
        self.failrepstr = self.getReportHeader(self.curShName, needscrips=True)
        self.repstr += self.getReportTableHeader()
        self.failrepstr += self.getReportTableHeader()
        try:
            startcolumnPos = 0
            heads, rowpos = self.getHeads(rowpos, startcolumnPos, ncols)
            self.heads = self.stripHeads(heads)  # strip space , '\n'
            self.colspan = len(self.heads)
            self.repstr += self.getReportTitle(self.title)
            self.failrepstr += self.getReportTitle(self.title)
            #self.processReportHeads()
            if self.note:
                self.repstr += self.getReporth2header(self.note, 'H4')
            if self.interface and self.function:
                self.repstr += self.getReporth2header(self.interface + self.function, 'H3')
                self.failrepstr += self.getReporth2header(self.interface + self.function, 'H3')
            self.repstr += self.getReportTableColumnName(self.heads)
            self.failrepstr += self.getReportTableColumnName(self.heads)
            self.defineVarAndTypeDict(self.heads)  # redefine variable type
#             if hasattr(self, 'testCaseId') == False:
#                 exec 'ExcelColumnFixture.testCaseId = 0'
            Log.debug('heads:', heads)
            self.bind(self.heads)
            row = rowpos
            while row < nrows:
                self.restInitVar()
                rowdata, row = self.doCells(row, startcolumnPos, ncols, nrows)
                self.repstr += self.getReportTableRow(rowdata)
                if self.results[self.testCaseId] == 'fail' :
                    self.failrepstr += self.getReportTableRow(rowdata)
            self.repstr += self.getReportTableTail()
            self.failrepstr += self.getReportTableTail()
            if self.isMakeReporterFlag:
                self.repstr += self.getReportTail(self.counts.toString())
                self.failrepstr += self.getReportTail()
                self.genHtmlfile(self.failrepstr, self.failReportFileName)
                self.genHtmlfile(self.repstr, self.reportFileName)
            self.saveCounts()
        except BaseException, e:
            Log.exception(e)
        self._clear()
        Log.debug('end: ExcelColumnFixture.doRows')

    def doCells(self, rowpos, startcolumnPos, ncols, nrows=None):
        Log.debug('start: ExcelColumnFixture.doCells')
        rowdata = ''
        for col in range(startcolumnPos, self.posDict['methodPos'] + 1):
            text = self.excelAPP.getCellStrValue(rowpos, col)
            cell = self.getCellStrValue(text)
            self.doCell(cell, col)
            if cell.text == '' or cell.text == ' ':
                cell.text = '&nbsp;'  # space
            rowdata = rowdata + cell.__str__()
        Log.debug('end: ExcelColumnFixture.doCells')
        return rowdata, rowpos + 1

    def doCell(self, cell, column):
        Log.debug('start: ExcelColumnFixture.doCell')
        a = self.columnBindings[column]
        text = str(cell.text)
        if a.shouldIgnore(text) == 1:
            pass
        elif a.shouldIgnore(text) == 2:
            self.ignore(cell)
        elif a.field:
            a.set(a.parse(text))
        elif a.method:
            self.check(cell, a)
        Log.debug('end: ExcelColumnFixture.doCell')
    
    def restInitVar(self):
        if hasattr(self, 'url'):
            self.url = ''
        if hasattr(self, 'expected'):
            self.expected = ''
                
    def resetReportFileName(self, reportFileName, sheetName):
        if reportFileName.find('.html') > -1:
                    reportFileName = reportFileName[:-5]
        self.curShName = sheetName
        filename = reportFileName + '_' + sheetName
        filename = filename.replace(' ', '_')
        self.reportFileName = REPORTPATH + filename + '.html'
        self.failReportFileName = FAILREPORTPATH + 'Fail_' + filename + '.html'

    def processHeads(self, rowpos, ncols):
        return rowpos

    def processReportHeads(self):
        pass

#===============================================================================
# get data
#===============================================================================
    def getCellStrValue(self, text):
        return Cell(text)

    def getFixturePath(self, rowpos, ncols):
        fixturePath = ''
        for col in range(0, ncols):
            temp = self.excelAPP.getCellStrValue(rowpos, col)
            if len(temp) > 1:
                if temp.find("fixture") > -1:  # $ means fixture row
                    fixturePath = temp
                    rowpos += 1
                break
        return fixturePath, rowpos

    def getTitle(self, rowpos, ncols):
        title = ''
        for col in range(ncols):
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

    # @return: headlist, rowpos       
    def getHeads(self, rowpos, startcolumnPos, ncols):
        Log.debug('start getHeads: ' + self._CLASSNAME)
        heads = []
        col = startcolumnPos
        while col < ncols:
            columnName = self.strip(self.excelAPP.getCellStrValue(rowpos, col))
            ##如果包含result关键字，表明此列为方法列
            if columnName.lower().find('expect') > -1 \
                or columnName.find('()') > -1:
                if columnName.lower().find('expect') > -1:
                    columnName = 'test()'  # test method interface
                    heads.append(columnName)
                self.posDict['methodPos'] = col
                break  # will remove
            else:
                heads.append(columnName)
                col += 1
        Log.debug('end getHeads: ' + self._CLASSNAME)
        return heads, rowpos + 1

    def defineVarAndTypeDict(self, heads):
        codestr = ''
        len1 = len(heads)
        sufix = "()"
        self._typeDict.clear()
        try:
            for i in range(len1):
                varname = heads[i]
                if varname[-len(sufix):] == sufix:
                    varname = varname[:-len(sufix)]
                else:
                    # setattr(self, varname, '')
                    codestr = codestr + 'ExcelColumnFixture.' \
                                      + varname + '="" \n'
                self._typeDict[varname] = 'str'  # add varname into type diction
            exec codestr
        except BaseException, err:
            Log.error(err)
            Log.debug(ExcelColumnFixture.__dict__)
        Log.debug('start getHeads: ' + self._CLASSNAME)

    def stripHeads(self, heads):
        len1 = len(heads)
        for i in range(len1):
            heads[i] = self.strip(heads[i])
        return heads

    def strip(self, name):
        result = ''
        try:
            name = name.replace(' ', '')
            result = name.replace('\n', '')
        except:
            pass
        return result

    def checkHeads(self, heads):
        result = True
        for head in heads:
            if len(head) == 0:
                print 'warning: maybe heads format of excel file is wrong!'
                print heads
                result = False
                break
        return result

    def saveCounts(self):
        if self.reportFileName:
            reportfilename = self.reportFileName.split(os.sep)[-1]
            self.summaryCounts[reportfilename] = self.counts
#         if self.failReportFileName:
#             failreportfilename = self.failReportFileName.split(os.sep)[-1]
#             self.summaryCounts[failreportfilename] = self.counts

#================================================================================
# bind 
#================================================================================
    def bind(self, heads):
        length = len(heads)
        self.columnBindings = [None] * length
        i = 0
        sufix = "()"
        for i in range(length):
            name = heads[i]
            if name[-len(sufix):] == sufix:
                self.columnBindings[i] = self.bindMethod(name[:-len(sufix)])
            else:  # name is field 
                self.columnBindings[i] = self.bindField(name)

    def bindMethod(self, name):
        classObj = self.getTargetClass()
        return adapterOnMethod(self, name, targetClass=classObj)

    def bindField(self, name):
        classObj = self.getTargetClass()
        return adapterOnField(self, name, targetClass=classObj)

    def getTargetClass(self):
        return self.__class__

#===============================================================================
#    make test result 
#===============================================================================
# public static void right (Parse cell) {
    def right(self, cell, actual=''):
        print 'testCaseId: ' + self.testCaseId + ' test pass'
        self.results[self.testCaseId] = "pass"
        cell.addToTag(" bgcolor=\"#cfffcf\"")
        self.counts.right += 1
        if actual:
            #cell.addToBody(self.escape(actual))
            actual = self.label("excepted: ") + self.escape(self.expected) + "<hr>" + \
                     self.label("actual: ") + self.escape(actual)
            cell.overrideToBody("<font size=2.0pt>%s</font>" % actual)

    # public static void output (Parse cell) {
    def output(self, cell, actual=''):
        print 'testCaseId: ' + self.testCaseId + ' test ok'
        self.results[self.testCaseId] = "pass"
        cell.addToTag(" bgcolor=\"#cfffcf\"")
        self.counts.right += 1
        if actual:
            cell.overrideToBody(actual)

    # public static void wrong (Parse cell) {
    # public static void wrong (Parse cell, String actual) {
    def wrong(self, cell, actual=''):
        print 'testCaseId: ' + self.testCaseId + ' test fail'
        self.results[self.testCaseId] = "fail"
        cell.addToTag(" bgcolor=\"#ffcfcf\"")
        self.counts.wrong += 1
        if actual:
            actual = self.label("excepted: ") + self.escape(self.expected) + "<hr>" + \
                     self.label("actual: ") + self.escape(actual)
            cell.overrideToBody("<font size=2.0pt>%s</font>" % actual)

    # public static void ignore (Parse cell) {
    def ignore(self, cell):
        cell.addToTag(" bgcolor=\"#efefef\"")        

    # public static void ignore (Parse cell) {
    def ignoreTest(self, cell):
        print 'testCaseId: ' + self.testCaseId + ' test ignore'
        cell.addToTag(" bgcolor=\"#efefef\"")
        cell.addToBody("Test case ignored!")
        self.counts.ignores += 1

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

    def escape(self, thestring, old=None, new=None) :
        if old == None:
            return self.escape(self.escape(thestring, '&', "&amp;"), '<', "&lt;")
        else:
            return str(thestring).replace(old, new)

    # run test
    def check(self, cell, a):
        Log.debug('start: ExcelColumnFixture.check')
        ignoreFlag = False
        if self.testCaseIdRangeFlag:  # execute test by test case id range
            Log.debug('testCaseIdRangeFlag is True')
            if hasattr(self, 'testCaseId') :
                ignoreFlag = False
                if self.testCaseId== self.testCaseIdStart:
                    self.startFlag = True
                if self.testCaseId== self.testCaseIdEnd:  # don't include testCaseIdEnd
                    self.endFlag = True
                if self.startFlag and self.endFlag is False:
                    ignoreFlag = False
                else:
                    ignoreFlag = True
                    if self.colspan is not None:
                        self.ignoreTest(cell)
        if ignoreFlag:
            return 
        self.runTest(cell, a)
        Log.debug('end: ExcelColumnFixture.check')
        
    def genHtmlfile(self, repstr, filename):
        Log.debug('start genHtmlfile: ' + self._CLASSNAME)
        try:
            try:
                outputReport = open(filename, 'w')
                outputReport.write(repstr)
                outputReport.flush()
                outputReport.close()
            except IOError, e:
                Log.error(e)
        finally:
            outputReport.close()
        Log.debug('end genHtmlfile: ' + self._CLASSNAME)

    def makeRepoter(self):
        Log.debug('start makeRepoter: ' + self._CLASSNAME)
        try:
            try:
                self.outputReport = open(self.reportFileName, 'w')
                self.outputReport.write(self.repstr)
                self.outputReport.flush()
                self.outputReport.close()
                #self.reportNameList.append(self.reportFileName)
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
            self.summaryReport = open(self.summaryReportName, 'w')
            self.repstr = self.getReportHeader('summary report')
            self.repstr += self.getReportTableHeader()
            columnNames = ['filepath', 'summary result', 'detail reporter url']
            self.repstr += self.getReportTableColumnName(columnNames)
            for reportName in self.reportNameList:
                try:
                    reportfilename = reportName.split(os.sep)[-1]
                    counts = self.summaryCounts[reportfilename]
                except BaseException, e:
                    Log.error(e)
                    counts = 'ERROR:NO DATA'
                countcell = Cell(counts)
                if (hasattr(counts, 'wrong') and counts.wrong == 0):
                    #green
                    countcell.addToTag(" bgcolor=\"#cfffcf\"")
                else:
                    countcell.addToTag(" bgcolor=\"#ffcfcf\"")
                #name = reportName.split(os.sep)[-1]
                linkcell = Cell('<a href=%s>link to html</a>' % reportfilename)
#                 try:
#                     filename = reportfilename[:-12]
#                 except:
#                     filename = 'filename'
                namecell = Cell(reportName)
                namecell.addToTag("align='left'")
                rowdata = namecell.__str__() \
                            + countcell.__str__() \
                            + linkcell.__str__()
#                 if self.ismonitorcpu:
#                     self.cpuChart = Cell('<a href=..\\%s>open cpu chart</a>' \
#                                      %self.cpuRatioChartMap[reportName])
                self.repstr += self.getReportTableRow(rowdata)
            self.repstr += self.getReportTail()
            self.summaryReport.write(self.repstr)
            self.summaryReport.flush()
            self.summaryReport.close()
            print 'make summary report ok'
        Log.debug('end makeSummaryReport: ' + self._CLASSNAME)

    def openFileReport(self, reportFileName=''):
        if not reportFileName:
            reportFileName = self.summaryReportName
        if os.path.exists(reportFileName)  and len(self.reportNameList) > 1:
            webbrowser.open_new(reportFileName)
        else:
            if self.reportNameList[0]:
                webbrowser.open_new(self.reportNameList[0])

    def openReport(self):
        Log.debug(self.reportNameList)
        for reportName in self.reportNameList:
            try:
                print reportName
                webbrowser.open_new(reportName)
            except BaseException, e:
                Log.exception(e)


class ExcelColumnFixtureException(Exception):
    pass


# from fit.Fixture
class Counts:

    def __init__(self):
        self.right = 0
        self.wrong = 0
        self.ignores = 0
        self.exceptions = 0

    def toString(self):
        return ("%s pass, %s fail, %s ignored, %s exceptions" %
                (self.right, self.wrong, self.ignores, self.exceptions))

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
        self.tag = '<td align=center>'

    def addToTag(self, text):
        self.tag = self.tag[:-1] + text + ">"

    def addToBody(self, text):
        if hasattr(self, 'text') and self.text:
            self.text = self.text + text
        else:
            self.text = text

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

