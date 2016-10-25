# -*- coding: UTF-8 -*-
'''
@author: Water
'''
from log.Log import Log


class Report(object):
    '''
    make report
    '''

    outputReport = None

    def __init__(self, outputReport):
        self.outputReport = outputReport

    def getReportHeader(self, titlename, outputReport=None, needscrips=False):
        title = "<html><meta charset='utf-8'/>\n<title>" + titlename + "</title>"
        script = ''
        body = "<body>"
        if needscrips == True:
            script = '''<script type="text/javascript">
                        function show(id){
                            var target=document.getElementById(id);
                            if(target.style.display == 'none'){//none表示隐藏起来的意思，也就说如果这个元素是隐藏起来的话
                                target.style.display='block';
                            }else{
                                target.style.display = 'none';
                            }
                        }
                        </script>'''
        return title + script + body

    def makeReportHeader(self, titlename, outputReport=None, needscrips=False):
        if outputReport == None:
            outputReport = self.outputReport
        outputReport.write("<html><meta charset='utf-8'/>\n")
        outputReport.write("<title>")
        try:
            outputReport.write(titlename)
        except:
            outputReport.write('automation testing')
        outputReport.write("</title>")
        if needscrips == True:
            script = '''<script type="text/javascript">
                        function show(id){
                            var target=document.getElementById(id);
                            if(target.style.display == 'none'){//none表示隐藏起来的意思，也就说如果这个元素是隐藏起来的话
                                target.style.display='block';
                            }else{
                                target.style.display = 'none';
                            }
                        }
                        </script>'''
            outputReport.write(script)
        outputReport.write("<body>")

    def getReportEnvInfo(self, envinfo, outputReport=None):
        pass

    def makeReportEnvInfo(self, envinfo, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        #outputReport.write('<H2>' + envinfo + '</H2>')

    def getReportTitle(self, title, outputReport=None):
        return '<H2><align=left>' + title + '</align></H2>'

    def getReporth2header(self, content, headerlevel='H4'):
        return '<%s><align=left>' % headerlevel \
                    + content + '</align></%s>' % headerlevel

    def makeReportTitle(self, title, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        title = title.replace('Testcases', 'Automation Testing')  # STRIP TEST CASE FROM REPORT TITLE
        # title = title.replace('Test Cases', '') 
        outputReport.write('<H2><align=left>' + title + '</align></H2>')
    
    def getReportTableHeader(self, outputReport=None):
        tableHeader =  '''<table border=1 cellspacing="0" cellpadding="0"  \
                                bordercolorlight="#006142" bordercolordark="#EFEFEF">\n'''
        return tableHeader

    def makeReportTableHeader(self, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        outputReport.write('''<table border=1 cellspacing="0" cellpadding="0"  \
                                bordercolorlight="#006142" bordercolordark="#EFEFEF">\n''')
        outputReport.write('<div align=left>\n') #

    def getReportTableColumnName(self, columnList=[], outputReport=None): 
        columnstr = '' 
        for columnName in columnList:
            columnstr = columnstr + "<td align=left>" + columnName + "</td>"
        return columnstr

    def makeReportTableColumnName(self, columnList=[], outputReport=None): 
        row = '' 
        for columnName in columnList:
            row = row + "<td align=left>" + columnName + "</td>"
        self.makeReportTableRow(row, outputReport)

    def getReportTableRow(self, row, outputReport=None):
        if not row:
            row = ''
        return "<tr>" + row + "</tr>\n"

    def makeReportTableRow(self, row, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        outputReport.write("<tr>" + row + "</tr>\n") 

    def getReportTableTail(self, outputReport=None):
        return "</table>\n"

    def makeReportTableTail(self, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        outputReport.write('</div>\n')
        outputReport.write("</table>\n") 

    def getReportTail(self, counts = None, outputReport=None):
        if counts:
            testResult = '<H2>Test Result: ' + counts + '</H2>\n</body>\n</html>\n'
        else:
            testResult = '\n</body>\n</html>\n'
        return testResult

    def makeReportTail(self, counts, outputReport=None):
        if outputReport == None:
            outputReport = self.outputReport
        try:
            testResult = 'Test Result: ' + counts.toString()
            outputReport.write('<H2>' + testResult + '</H2>\n')
        except BaseException, e:
            Log.debug('counts')
            Log.debug(e)
        outputReport.write("</body>\n")
        outputReport.write("</html>\n")