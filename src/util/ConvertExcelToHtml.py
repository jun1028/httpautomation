'''

@author: water.zhang
'''

import os, sys
import util.excel
import runner.GlobalSetting
from log.Log import Log

class ConvertExcelToHtml(object):
    
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    #predefine:the first row of the excel must be title
    #          the second row must be test class name
    #          the third row must be column name
    #          the fourth row must be column value
    #Pre-expand: after that ,will append function column ,the fixture dependence
    #            on special function, ,and now if need convert to html table,
    #            at first you must write the fixture row.
    #like this excel work sheet:
    #    -----------------------------------------------------------------
    #    |Title:Regression TestCases on STAT
    #    -----------------------------------------------------------------
    #    |Fixture name: write fixture name by manual
    #    -----------------------------------------------------------------
    #    |parameter:TestCaseNumber |DoNotDeleteTestFiles |TestIOSizeKB |ReadIOSizeKB
    #    -----------------------------------------------------------------
    #    |value:2                  |1                    |512          |1024    
    #    |...                      |...                  |...          |...    
    #    -----------------------------------------------------------------
    def convertExcelToHtml(self, filename, lShNames = None, specifyHtmlPath = None):
        Log.debug('ConvertExcelToHtml.convertExcelToHtml(), convert Excel ' + filename + ' to html file')
        excelRD = util.excel.ExcelAppRD()
        excelRD.open(filename)
        title = ''
        columns = []
        # create html file
        if len(filename) <= 0:
            print 'convertExcelToHtml: filename is null, please make sure filename is correct'
            Log.debug('convertExcelToHtml: filename exception')
            os._exit()
        htmlFilePath = filename.split('.')[-2]  # get file path,it is same as the excel file
        htmlFilePathTuple = htmlFilePath.split('\\')    #split file name, path
        if specifyHtmlPath is not None:
            htmlFilePath = specifyHtmlPath
        else:   # default folder root folder\testcases\
            if os.path.exists('testcases\\') is not True:
                os.mkdir('testcases\\')
            htmlFilePath = 'testcases\\' + htmlFilePathTuple[-1] + '.html'
        infile = open(htmlFilePath, 'w')
        # end create html file
        # write excel file data to table of html file 
        infile.write("<html>\n")
        infile.write("<title>")
        try:
            infile.write(excelRD.lShNames[0])
        except:
            infile.write('automation testing')
        infile.write("</title>")
        infile.write("<body>")
        if lShNames is None:
            lShNames = excelRD.lShNames
        Log.debug('lshNames: ' + str(lShNames))
        for shname in lShNames:
            sheet = excelRD.getShByName(shname)
            excelRD.setSheet(sheet)
            if sheet == None:
                print shname + ' of GLOBALSETTING SHEETS is not correct, please specify a correct sheets name'\
                        + 'please modify sheets of GLOBALSETTING.py, clear the value, wiil excute all of sheet in excel'
                sys.exit(0)
            ncols = sheet.ncols
            nrows = sheet.nrows
            if ncols == 0 or nrows == 0:
                break                        
            # get title from the first row
            rowpos = 0  #
            for col in range(ncols):
                tl = excelRD.getCellStrValue(rowpos, col)
                if len(tl) > 1:
                    title = str(tl)
                    title = title.replace('TestCases', 'test')
                    title = title.replace('Test Cases', 'test')
                    title = title + ' Report'
                    title = title.title()
                    rowpos += 1
                    break
            infile.write('<H2>'+title +'</H2>')
            infile.write('''<table border=1 cellpadding=0 bordercolorlight="#000000" bordercolordark="#FFFFFF">\n''')
            infile.write('<div align=center>\n')        
            colpos = 0       
            # get test class name,fixture name,the second row, self.setFixtureName(fixtureName, colspan)      
            for col in range(ncols):
                 fixturename = excelRD.getCellStrValue(rowpos, col)
                 if len(fixturename) > 1:
                     colpos = col
                     rowpos += 1
                     colspan = str(ncols - colpos)
                     infile.write("<tr>") 
                     infile.write("<td align=left colspan="+colspan+">" + fixturename + "</td>")
                     infile.write("</tr>\n")
                     break        
            self.writeTableBodyToFile(excelRD, infile, colpos, rowpos, ncols, nrows)
            # end for excelRD.numOfShs
            infile.write('</div>\n')
            infile.write("</table>\n") 
        infile.write("</body>\n")      
        infile.write("</html>\n")
        # end write excel file data
        infile.flush()
        infile.close()
        Log.debug('end: ConvertExcelToHtml.convertExcelToHtml')
        return htmlFilePath
    
    def writeTableBodyToFile(self, excelRD, infile, colpos, rowpos, ncols, nrows):
        Log.debug('start: ConvertExcelToHtml.writeTableBodyToFile')
        infile.write("<tr>") 
        actualPos = None    # record Actual column position
        commentPos = None   # record comment column position
        testerPos = None
        buildverPos = None
        expectedPos = None
        methodPos = None
        methodflag = False
        # get column name,the third row
        for col in range(colpos, ncols):
             columnName = excelRD.getCellStrValue(rowpos, col)
             if len(columnName) > 1:
                 if columnName == 'Results' or columnName == 'results' \
                        or columnName == 'Result' or columnName == 'result':
                     columnName = 'test()'    # test method interface
                     methodflag = True
                     methodPos = col
                 # the columName is Actual,ignore it,the Actual value will fill in Results column
                 if columnName.find('Actual') > -1:  
                     actualPos = col    
                     continue   # replace by test() column
                 if columnName.find('Comment') > -1:  
                     commentPos = col
                     continue   # comment don't need write to table
                 if columnName.find('Tester') > -1:  
                     testerPos = col
                     continue   # Tester don't need write to table
                 if columnName.find('Expected') > -1:  
                     expectedPos = col
                     continue   # Expected don't need write to table
                 if columnName.find('Build') > -1:  
                     buildverPos = col
                     continue
                 Log.debug('column name: ' + str(columnName))
                 infile.write("<td align=center>" + columnName + "</td>")
                 if methodflag:
                     break
        infile.write("</tr>\n")
        #get column data
        rowpos += 1
        for row in range(rowpos, nrows):
            infile.write("<tr>")
            try:
                for col in range(colpos, methodPos + 1):
                    if col == actualPos:
                        continue
                    if col == commentPos:
                        continue
                    if col == testerPos:
                        continue
                    if col == expectedPos:
                        continue
                    if col == buildverPos:
                        continue
                    columValue = excelRD.getCellStrValue(row, col)
                    if columValue == '' or columValue == ' ':
                        columValue = '&nbsp;'   # space
                    infile.write("<td align=center> " + str(columValue) + "</td>")
            except BaseException, e:
                print e
            infile.write("</tr>\n") 
        Log.debug('end: ConvertExcelToHtml.writeTableBodyToFile')
    
        #DEFINE EXPAND HEADS
    def getExpandheads(self, style):
        expandHeads = '<font size = 2.0pt><td ' + style + '>ClientID</td> \
                        <td ' + style + '>Instance</td> \
                        <td ' + style + '>Read RateMBPS Avg</td> \
                        <td ' + style + '>Read TimeMS Sess Avg</td>\
                        <td ' + style + '>Write RateMBPS Avg</td>\
                        <td ' + style + '>Write TimeMS Sess Avg</td>'
        return expandHeads
        

class ConvertExcelOfMulInstanceToHtml(ConvertExcelToHtml):
    '''
    classdocs
    '''

    def writeTableBodyToFile(self, excelRD, infile, colpos, rowpos, ncols, nrows):
        Log.debug('start: ConvertExcelOfMulInstanceToHtml.writeTableBodyToFile')
        instancename = None # instance section name
        paramcount = 0  # param count of instance,count of every instance should equal
        count = 0
        actualPos = None   # record Actual column position
        commentPos = None   # record comment column position
        testerPos = None
        buildverPos = None
        expectedPos = None
        serveraddressPos = None
        clientoperationsystemPos = None
        colNameAfterInstanceList = runner.GlobalSetting.COLNAMEAFTERINSTANCELIST
        #get column name,the third row
        infile.write("<tr>") 
        for col in range(colpos, ncols):
            columnName = excelRD.getCellStrValue(rowpos, col)
            if columnName == 'Server Address':
                serveraddressPos = col
                continue
            if columnName == 'Client Operation System':
                clientoperationsystemPos = col
                continue
            if columnName.find('Result') > -1:
                columnName = 'test()'    # test method interface
            #the columnName is Actual,ignore it,the Actual value will fill in Results column
            if columnName.find('Actual') > -1:  
                actualPos = col    
                continue   # replace by test() column
            if columnName.find('Comment') > -1:  
                commentPos = col
                continue   # comment don't need write to table
            if columnName.find('Tester') > -1:  
                testerPos = col
                continue   # Tester don't need write to table
            if columnName.find('Expected') > -1:  
                expectedPos = col
                continue   # Expected don't need write to table
            if columnName.find('Build') > -1:  
                buildverPos = col   
                continue            
            if count > 0:
                columnName = instancename + '_ ' + excelRD.getCellStrValue(rowpos + 1, col)
                count -= 1
            elif columnName.find('Instance-') > -1:
                instancename = columnName
                if paramcount == 0:  
                    curCol = col
                    # calculate  param count, the count equals columns of next instance - columns of current instance          
                    for col in range(curCol + 1, ncols):
                        temp = excelRD.getCellStrValue(rowpos, col)
                         # find out next instance or read column after instance
                        if temp.find('Instance-') > -1 or temp in colNameAfterInstanceList:
                            next = col
                            paramcount = next - curCol
                            break 
                    col = curCol
                instancename = instancename.replace('-', ' _')
                columnName = instancename + '_ ' + excelRD.getCellStrValue(rowpos + 1, col)
                count = paramcount - 1     
            Log.debug(str(columnName))
            infile.write("<td align=center>" + columnName + "</td>")
        infile.write("</tr>\n")
        rowpos += 2
        #get column data
        for row in range(rowpos, nrows):
            infile.write("<tr>")
            try:
                for col in range(colpos, ncols):
                    if col == actualPos:
                        continue
                    if col == commentPos:
                        continue
                    if col == testerPos:
                        continue
                    if col == expectedPos:
                        continue
                    if col == serveraddressPos:
                        continue                    
                    if col == clientoperationsystemPos:
                        continue  
                    if col == buildverPos:
                        continue                                      
                    columValue = excelRD.getCellStrValue(row, col)
                    if columValue == '' or columValue == ' ':
                        columValue = '&nbsp;'   # space
                    infile.write("<td align=center> " + str(columValue) + "</td>")
            except BaseException, e:
                print e
            infile.write("</tr>\n")
        Log.debug('end: ConvertExcelOfMulInstanceToHtml.writeTableBodyToFile')

if __name__ == '__main__':
    convertExcelToHtml = None
    filename = None
    multipleInstanceFlag = False
    htmlpath = None
    argv = sys.argv
    print 'convert excel file into html file'
    if len(argv) == 1:
            sys.stderr.write("usage: python filename param[m means multiple instance]\n")
            sys.exit(-1) 
    if len(argv) > 1:
        filename = argv[1]
    if len(argv) > 2:
        htmlpath = argv[2]
    if len(argv) > 3:
        multipleInstanceFlag = True    
    if multipleInstanceFlag:      
       convertExcelToHtml = ConvertExcelOfMulInstanceToHtml()
    else:
        convertExcelToHtml = ConvertExcelToHtml()
    convertExcelToHtml.convertExcelToHtml(filename, specifyHtmlPath = htmlpath)
    
    
    
    