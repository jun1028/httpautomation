# -*- coding: UTF-8 -*-
# package: fixture.FliterExcelColumnFixture
'''

@author: Water.Zhang
'''

from fixture.ExcelColumnFixture import ExcelColumnFixture


class FliterExcelColumnFixture(ExcelColumnFixture):
    
    """
    read excel file, execute test by invoke HTTP interface, and generate HTML report
    """
    
    comments = ['note', 'Note', 'comment', 'Comment'] #
    interface = ''  # http url, like http://www.xxx.com:8080/path
    function = ''
    argCounts = 0
    note = ''
    
    _typeDict = {"actualResult": "str",
                 "test":'str'}
    
    def processHeads(self, rowpos, ncols):
        self.interface, rowpos = self.getInterface(rowpos, ncols)
        self.function, rowpos = self.getFunction(rowpos, ncols)
        self.argCounts, rowpos = self.getArgCounts(rowpos, ncols)
        self.note, rowpos = self.getComment(rowpos, ncols) 
        return rowpos
    
    def processReportHeads(self):
        if self.note != '':
                self.makeReportTableNoteRow(self.note, self.outputReport)   
        self.makeReportTableInterface(self.interface + self.function, self.outputReport)
        self.makeReportTableInterface(self.interface + self.function, self.failOutputReport)
        
    
        # @return: interface, rowpos
    def getInterface(self, rowpos, ncols):
        interface = ''
        for col in range(0, ncols):
            interface = self.excelAPP.getCellStrValue(rowpos, col)
            if len(interface) > 1 and interface.find('Interface') > -1:
                interface = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return interface, rowpos
    
    # @return: function, rowpos
    def getFunction(self, rowpos, ncols):
        function = ''
        for col in range(0, ncols):
            function = self.excelAPP.getCellStrValue(rowpos, col)
            if len(function) > 1 and function.find('Function') > -1:
                function = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return function, rowpos
    
    # @return: interface, rowpos
    def getArgCounts(self, rowpos, ncols):
        argCounts = 0
        for col in range(0, ncols):
            argCounts = self.excelAPP.getCellStrValue(rowpos, col)
            if len(argCounts) > 1 and argCounts.find('ArgCount') > -1:
                argCounts = self.excelAPP.getCellStrValue(rowpos, col + 1)
                rowpos += 1
                break
        return argCounts, rowpos
    
    # @return: note, rowpos
    def getComment(self, rowpos, ncols):
        note = ''
        while True:  # multiple rows comment
            noteFlag = False
            for col in range(0, ncols):
                temp = self.excelAPP.getCellStrValue(rowpos, col)
                if len(temp) > 1 :
                    for comment in self.comments:
                        if temp.find(comment) > -1:
                            note = note + temp
                            noteFlag = True
                            break
                continue
            if noteFlag : rowpos += 1
            else:break
        return note, rowpos
   
        

