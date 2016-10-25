# -*- coding: UTF-8 -*-
# package: fit.ExcelAppRD
'''

@author: Water.Zhang
'''

import os
import xlrd

class ExcelAppRD(object):
    
    '''
      Read from  Excel data
    '''
    
    numOfShs = 0
    lShNames = []
    curSheet = None # current Sheet class 
    
    __xlBook = None
        
    def openExcel(self, filename, filepath = None):
        try:
            if filepath is not None:
                filename = filepath + filename
            else:
                filename = os.path.abspath(filename)
                print filename     
            if os.path.exists(filename):  
                print 'openExcel excel file'
                self.__xlBook = xlrd.open_workbook(filename)
                self.numOfShs = self.__xlBook.nsheets
                self.lShNames = self.__xlBook.sheet_names()
                self.curSheet = self.__xlBook.sheet_by_index(0)
            else:
                print str(filename) + "Error: Excel File not exist in this path" 
                raise IOError
        except BaseException, e:
            print e
            
    def getShNameList(self):
        return self.lShNames
        
    def getShByName(self, name):
        sheet = None
        try:
            sheet = self.__xlBook.sheet_by_name(name)
            self.setSheet(sheet)
        except BaseException, e:
            print e
            print 'specify sheet does not exist'
        return sheet
            
    def getShByIndex(self, index):
        sheet = None
        try:
            sheet = self.__xlBook.sheet_by_index(index)
            self.setSheet(sheet)
        except IndexError, e:
            print 'index error,the max index is:' + str(self.numOfShs)
            print e
        return sheet
    
    def getCell(self, row, col, sheet = None):
        cell = None
        if sheet is None:
            sheet = self.curSheet
        try:
            cell = sheet.cell(rowx=row, colx=col)
        except BaseException, e:
            print e
        return cell
         
    def getCellStrValue(self, row, col, sheet = None):
        value = ''
        if sheet is None:
            sheet = self.curSheet
        try:
            value = self.convertToStr(sheet.cell_type(rowx=row, colx=col), sheet.cell_value(rowx=row, colx=col))
        except BaseException, e:
            print e
        return value
        
    def getCurSheet(self):
        return self.curSheet
    
    def getnRows(self, sheet = None):
        return self.curSheet.nrows
    
    def getnCols(self, sheet = None):
        return self.curSheet.ncols 
    
    def getRow(self, index, sheet = None):
        rows = None
        if sheet is None:
            sheet = self.curSheet
        rows = sheet.row(index)
        return rows
    
    def setSheet(self, sheet):
        self.curSheet = sheet 
        
#     Type symbol     Type number Python value 
#     XL_CELL_EMPTY   0           empty string u'' 
#     XL_CELL_TEXT    1           a Unicode string 
#     XL_CELL_NUMBER  2           float 
#     XL_CELL_DATE    3           float 
#     XL_CELL_BOOLEAN 4           int; 1 means TRUE, 0 means FALSE 
#     XL_CELL_ERROR   5           int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code 
#     XL_CELL_BLANK   6           empty string u''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used. 
    def convertToStr(self, cellType, cellValue):
        value = ''
        if cellType == 0 or cellType == 6:
            pass
        elif cellType == 1:
            value = cellValue
        elif cellType == 2:
            value = str(int(cellValue))
        elif cellType == 3: ###need rewrite 
            value = str(float(cellValue))   
        elif cellType == 4:
            value = str(bool(cellValue))    
        else:
            value = str(cellValue)   
        return value
         
                       
if __name__ == "__main__":
    test = ExcelAppRD()
    test.openExcel('test.xlsx')
    sheet = test.getShByIndex(0)
    for rx in range(sheet.nrows):
        print sheet.row(rx)
    print test.getCellStrValue(6, 4, sheet)
    print test.getCellStrValue(6, 0, sheet),
    print test.getCellStrValue(7, 4, sheet)
    print test.getCellStrValue(7, 0, sheet)
    print test.curSheet.name
    print test.getRow(0)
    #sheet = test.getShByName(u'stat')
        
