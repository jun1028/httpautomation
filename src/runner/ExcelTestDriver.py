# -*- coding: UTF-8 -*-
# package: runner.ExcelTestDriver
'''
@author: Water.Zhang
'''


import datetime
import os, sys
import types
import GlobalSetting
from fixture.ExcelColumnFixture import ExcelColumnFixture
from log.Log import Log
import util.excel

#UnicodeEncodeError: 'ascii' codec can't encode characters
reload(sys)
sys.setdefaultencoding('utf-8')

class ExcelTestDriver(object):
    '''
    classdocs
    '''
    infilename = None

    def __init__(self, argv):
        if len(argv) < 2:
            sys.stderr.write("usage: python input-file(test case excel file) output-file(test report name)\n")
            sys.exit(-1)
        self.infilename = argv[1]

    def __call__(self):
        self.setUp()
        self.runTest()
        self.tearDown()
        self.exit()

    def runTest(self):
        Log.debug('start: ExcelTestDriver.runTest')
        fixture = None
        starttime = datetime.datetime.now()
        runTime = 0
        iterationCount = GlobalSetting.ITERATION
        if type(iterationCount) != types.IntType:
            iterationCount = 0
        count = 0
        while True:
            count += 1
            fixture = ExcelColumnFixture()
            excelAPP = util.excel.ExcelAppRD()
            excelAPP.openExcel(self.infilename)
            print 'now start to test......'
            reportFileName = 'report'
            if count > 1:
                reportFileName = 'report' + str(count)
            fixture.dosheets(excelAPP, reportFileName)
            endtime = datetime.datetime.now()
            runTime = (endtime - starttime).seconds
            print 'run time(seconds) is: ' + str(runTime)
            #Log.debug('open report ' + str(fixture.reportNameList))
            fixture.openFileReport()
            if GlobalSetting.RUNTIME > 0:
                if runTime > GlobalSetting.RUNTIME:
                    break
            elif iterationCount < 1:
                break
            iterationCount -= 1
        Log.debug('end: ExcelTestDriver.runTest')

    #public void setup() {...}
    #initialize test environment, prepare test data,set environment variable.....      
    def setUp(self):
        print 'set up(initial) test environment'

    def tearDown(self):
        print 'tear down environment'
        Log.close()

    def exception(self, e):
        pass

    def exit(self):
        try:
            print 'test over'
            os._exit(0)
        except:
            pass

    run = __call__

if __name__ == '__main__':
    test = ExcelTestDriver(sys.argv).run()
