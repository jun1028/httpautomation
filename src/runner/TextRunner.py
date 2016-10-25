# -*- coding: UTF-8 -*-
# package: fixture.FliterFixture
'''

@author: Water.Zhang
'''

import sys, os
import time, datetime
import types

from fixture.TextFixture import TextFixture
from log.Log import Log
from runner import GlobalSetting


class TextRunner():
    
    '''
    run all test cases of html tables
    support stress test
    '''
    textfilename = ''
    outreportname = ''
    
    def __init__(self, argv):
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
        if len(argv) < 2:
            sys.stderr.write("usage: python input-file output-file\n")
            sys.exit(-1)
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
        if len(argv) == 2:
            self.outreportname = time.strftime('%Y-%m-%d-%H-%M-%S') + 'report.html'
        elif(len(argv) > 2):
            self.outreportname = argv[2]
            
        self.textfilename = argv[1]
    
    def __call__(self):
        self.setUp()
        self.runTest()
        self.tearDown()
        print 'the test report name is: %s, please review' % (self.outreportname)
        try:
            #if have not iteration, open report by automatic
            if GlobalSetting.ITERATION == 0 and GlobalSetting.RUNTIME == 0:
#                 webbrowser.open_new(self.outreportname)   # open test report
                pass
        except:
            pass
        self.exit()
        print 'call over' 
    
    def runTest(self):
        Log.debug('start: DcgFixture.runTest')
        print 'now start to test......'
        starttime = datetime.datetime.now()
        runTime = 0
        try:
            Log.info('iteration count: ' + str(GlobalSetting.ITERATION))
            iterationCount = GlobalSetting.ITERATION
            if type(iterationCount) != types.IntType:
                iterationCount = 0
            while True:       
                path = 'reports\\'
                if not os.path.exists(path):
                    os.mkdir(path)   
                dcg = TextFixture() 
                dcg.doTextTest(self.textfilename, path + self.outreportname)
                endtime = datetime.datetime.now()
                runTime = (endtime - starttime).seconds
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
        except (KeyboardInterrupt, SystemExit), e:
                print 'user Interrupt test'
                Log.exception(e)
                os._exit(0)
        except BaseException, e:
            print e
            Log.exception(e)
            os._exit(0)
        Log.debug('end: HtmlRunner.runTest')
        return 
                
    def setUp(self):
        print 'set up(initial) test environment'
        
    def tearDown(self):
        print 'test down environment'
        Log.close()
        
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
    TextRunner(sys.argv).run()
    
    
