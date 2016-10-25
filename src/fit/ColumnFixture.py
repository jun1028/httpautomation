"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

# 2003/07/23 2002/10/07.1 Fix ignoring for columns with no field or method.
#       A column with a blank head is a comment, and all cells will have
#       a default white background. A column whose field or method name
#       begins with a "?" is not implemented. Any cell with content will
#       be ignored, any cell without content will be skipped.
#        water.zhang modify bind()

import string, re, time
from log.Log import Log
from fit.Parse import Parse
from fit.Fixture import Fixture
from fit.TypeAdapter import adapterOnField, adapterOnMethod

class NoSuchMethodException(Exception):
    pass

class ColumnFixture(Fixture):
    """
    """
    results = {}  # result of each test case
    columnBindings = []

    ## Traversal ################################

    def doRows(self, rows, expandColumnsTag = None):
        self.bind(rows.parts, expandColumnsTag)
        Fixture.doRows(self,rows.more)
            
    def doCell(self, cell, column):
        a = self.columnBindings[column]
        try:
            if not a.method: # method column includes 2 rows result row, data row
                if hasattr(self, 'rowspan'):
                    cell.addToTag(' rowspan=' + str(self.rowspan))
        except:
            pass
        try:
            text = cell.text()
            if a.shouldIgnore(text) == 1:
                pass
            elif a.shouldIgnore(text) == 2:
#            if not a:
                self.ignore(cell)
            elif a.field:
                if text:
                    a.set(a.parse(text))
            elif a.method:
                self.check(cell, a)
        except Exception, e:
            self.exception(cell, e)

    ## Utility ##################################

    def bind (self, heads, expandColumnsTag = None):
        self.columnBindings = [None] * heads.size()
        i = 0
        while heads:
            name = heads.text()
            # strip ' ','\n'
            name = name.replace(' ', '')
            name = name.replace('\n','')
            sufix = "()"
            try:
                if name[-len(sufix):] == sufix:
                    self.columnBindings[i] = \
                        self.bindMethod(name[:-len(sufix)])
                    if expandColumnsTag is not None: 
                        setattr(self, 'rowspan', 2) # added  in  2009/08/21, the first row means show test result, second test data      
                        style = heads.getStyle()
                        if style is None:
                            style = ''
                        try:
                            heads.addToBody(self.getExpandheads(style))
                        except AttributeError, e:
                            Log.info('please implement getExpandheads()!')
                            Log.exception(e)
                else: # name is field 
                    self.columnBindings[i] = self.bindField(name)
            except Exception, e:
                self.exception(heads, e)
            heads = heads.more
            i += 1
                
    def bindMethod(self, name):
        classObj = self.getTargetClass()
        return adapterOnMethod(self, name, targetClass = classObj)

    def bindField (self, name):
        classObj = self.getTargetClass()
        return adapterOnField(self, name, targetClass = classObj)

    def getTargetClass(self): # overridden in RowFixture and derived classes
        return self.__class__
