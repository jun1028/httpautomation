'''

@author: Water
'''
from fit.Fixture import Counts
from log.Log import Log
from util.Report import Report

class TextFixture(object):
    '''
    classdocs
    '''
    counts = Counts()
    summary = {}
    results = {}
    testCaseId = 1
    readedLines = 0
    urlpath = ''
    
    def __init__(self):
        pass
    
    def doTextTest(self, textFileName, reportname):
        self.textFileName = textFileName
        self.reportname = reportname
        file_object = open(self.textFileName, 'r')
        try:
            fixturePath = str(file_object.readline())
            fixturePath = self.strip(fixturePath)
            self.urlpath = self.strip(file_object.readline())
            if self.urlpath.find('url:') > -1:
                self.urlpath = self.urlpath.split(':')[-1]
                self.readedLines += 1
            else:
                self.urlpath = ''
            print fixturePath
            if fixturePath.find('fixture') == -1:  # if have not fixture row, use default fixture
                fixturePath = 'fixture.TextFixture'
            else:
                self.readedLines += 1
            clas = fixturePath.split('.')[-1]
            # fix for illegal Java trick in AllFiles. Frankly, I like it!
            i = fixturePath.split('$')
            try:
                if len(i) == 1:
                    exec 'import ' + fixturePath
#                     # test class method
                    exec 'fixture = ' + fixturePath + '.' + clas + '()' 
                else:
                    exec "import %s" % (i[0],)
                    exec "fixture = %s.%s()" % (i[0], i[1])
            except ImportError, e:
                Log.exception(e)
                print 'fixturePath does not exists'
                print 'system exit'
                return
            fixture.fixturePath = fixturePath
            fixture.textFileName = self.textFileName
            fixture.reportname = self.reportname
            fixture.readedLines = self.readedLines
            fixture.urlpath = self.urlpath
            fixture.runTest()
        finally:
            file_object.close()   
    
    def strip(self, s):
        s = s.strip()
        s=s.encode("ascii","ignore")
        return s
        
    def runTest(self):
        print 'need write test fixture'
    
if __name__ == "__main__":
    print 'ddd'
        
