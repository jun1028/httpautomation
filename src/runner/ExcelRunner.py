# -*- coding: UTF-8 -*-
# package: fit.ExcelColumnFixture
'''

@author: Water.Zhang
'''

import os, sys, time, stat

import GlobalSetting
from log.Log import Log
from runner import HtmlRunner
from util.ConvertExcelToHtml import ConvertExcelToHtml, ConvertExcelOfMulInstanceToHtml


class ExcelRunner(HtmlRunner):
    
    '''
    support excel file input
    covert excel to html file
    '''
    
    def __init__(self, argv, multipleInstanceFlag = False):
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
        self.expandColumnsTag = 'colspan=21'
        if len(argv) < 2:
            sys.stderr.write("usage: python input-file output-file\n")
            sys.exit(-1)
        if len(argv) == 2:
            self.outreportname = 'reports\\' + time.strftime('%Y-%m-%d-%H-%M-%S') + 'report.html'
            argv.append(self.outreportname)
        elif(len(argv) > 2):
            self.outreportname = argv[2]
            
        infilename = self.convertExcelToHtml(argv[1], multipleInstanceFlag)
        Log.info('html file: ' + infilename)      
        infile = open(infilename,'r')
        modtime = time.ctime(os.fstat(infile.fileno())[stat.ST_MTIME])
        try:
            self.outfile = open(argv[2],'w')
        except IOError:
            os.mkdir('reports\\')
            self.outfile = open(argv[2],'w')
        self.fixture.summary["input file"] = os.path.abspath(argv[1])
        self.fixture.summary["input update"] = modtime
        self.fixture.summary["output file"] = os.path.abspath(argv[2])
        self.input = infile.read()
        infile.close()
        self.output = self.outfile
        
    def convertExcelToHtml(self, filename, multipleInstanceFlag = False):
        convertExcelToHtml = None
        lShNames = None
        if multipleInstanceFlag:
            convertExcelToHtml = ConvertExcelOfMulInstanceToHtml()
        else:
            convertExcelToHtml = ConvertExcelToHtml()
        Log.debug('GlobalSetting.SHEETS:' + str(GlobalSetting.SHEETS))
        if len(GlobalSetting.SHEETS) > 0:
            lShNames = GlobalSetting.SHEETS   
        return convertExcelToHtml.convertExcelToHtml(filename, lShNames)

if __name__ == '__main__':
    test = ExcelRunner(sys.argv).run()
    

    