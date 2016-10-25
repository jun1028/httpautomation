'''
@author: water
'''

import os, sys, stat
import types
import time,datetime
import webbrowser
import GlobalSetting
from log.Log import Log
from fit.Parse import Parse
from fit.Fixture import Fixture

class HtmlRunner():
    
    '''
    run all test cases of html tables
    support stress test
    '''
    
    input = None
    tables = None
    fixture = Fixture()
    output = None
    outfile = None
    expandColumnsTag = None    #expand html table column, like 'colspan=23'
    outreportname = None
    
    def __init__(self, argv):
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
        if len(argv) < 2:
            sys.stderr.write("usage: python input-file output-file\n")
            sys.exit(-1)
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
        if len(argv) == 2:
            self.outreportname = 'reports\\' + time.strftime('%Y-%m-%d-%H-%M-%S') + 'report.html'
            argv.append(self.outreportname)
        elif(len(argv) > 2):
            self.outreportname = argv[2]
        infile = open(argv[1],'r')
        modtime = time.ctime(os.fstat(infile.fileno())[stat.ST_MTIME])
        self.outfile = open(argv[2],'w')
        self.fixture.summary["input file"] = os.path.abspath(argv[1])
        self.fixture.summary["input update"] = modtime
        self.fixture.summary["output file"] = os.path.abspath(argv[2])
        self.input = infile.read()
        infile.close()
        self.output = self.outfile
    
    def __call__(self):
        self.setUp()
        self.runTest()
        self.tearDown()
        print 'the test report name is: %s, please review' % (self.outreportname)
        try:
            #if have not iteration, open report by automatic
            if GlobalSetting.ITERATION == 0 and GlobalSetting.RUNTIME == 0:
                webbrowser.open_new(self.outreportname)   # open test report
                #pass
        except:
            pass
        self.exit()
        print 'call over' 
    
    def runTest(self):
        Log.debug('start: HtmlRunner.runTest')
        tags = ("html","table", "tr", "td")
        print 'now start to test......'
        starttime = datetime.datetime.now()
        runTime = 0
        try:
            Log.info('iteration count: ' + str(GlobalSetting.ITERATION))
            iterationCount = GlobalSetting.ITERATION
            if type(iterationCount) != types.IntType:
                iterationCount = 0
            count = 0
            while True:          
                self.tables = Parse(self.input, tags)   # look for html tag enclosing tables
                self.fixture.doTables(self.tables.parts, self.expandColumnsTag)
                self.output.write(str(self.tables))
                self.output.flush()
                self.output.close()
                endtime = datetime.datetime.now()
                runTime = (endtime - starttime).seconds
#===============================================================================
#                if runTime < 10:
#                    print 'run time is less than 10 second, maybe run STAT occur error,system exit'
#===============================================================================
                print 'run time(seconds) is: ' + str(runTime)
                try:
                    if GlobalSetting.RUNTIME > 0:
                        if runTime > GlobalSetting.RUNTIME:
                            break
                    elif iterationCount < 1:
                        break
                except BaseException, e:
                    Log.exception(e)
                    break              
                iterationCount -= 1
                if GlobalSetting.NEEDREPORTS:
                    temp = self.outreportname.split('.')[-2]  # get file path
                    pathTuple = temp.split('\\')    #split file name, path              
                    count += 1  
                    if os.path.exists('reports\\') is not True:
                        os.mkdir('reports\\')
                    report = 'reports\\' + pathTuple[-1] + '(' + str(count) + ')' + '.html'
                    self.output = open(report, 'w')
        except (KeyboardInterrupt, SystemExit), e:
                print 'user Interrupt test'
                Log.exception(e)
                os._exit(0)
        except BaseException, e:
                self.exception(e)
                Log.exception(e)
                os._exit(0)
        Log.debug('end: HtmlRunner.runTest')
        return 
                
    def setUp(self):
        print 'set up(initial) test environment'
 
    def tearDown(self):
        print 'test down environment'
        Log.close()
        
    def exception(self,e):
        tables = Parse(tag="body",
                       body="Unable to parse input. Input ignored.",
                       parts=None,
                       more=None)
        Fixture.exception(self.fixture, tables, e)
        
    def exit(self):
        try:
            #self.outfile.close()
            sys.stderr.write(self.fixture.counts.toString()+'\n')
            print 'test over'
            os._exit(0)
            print 'can not reach!'
        except:
            pass 
    
    run = __call__
    
if __name__ == '__main__':
    HtmlRunner(sys.argv).run()

