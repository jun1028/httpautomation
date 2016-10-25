# -*- coding: UTF-8 -*-
'''
@author: water
'''

class HtmlTable(object):
    '''
        实现对所有类型的测试数据封装成标准的HTML TABLE
    '''
    curCols = 0
    curRows = 0
    tables = None
        
    def __init__(self):
        '''
        Constructor
        '''
    def openFile(self, filepath):
        pass
    
    def getTableByName(self, tableName):
        pass
    
    #获取所有的table name
    def getTableNames(self):
        pass
    
    def getCellStrValue(self, row, col):
        pass
    
    def getTableByIndex(self, index):
        pass
