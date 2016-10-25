"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

import string, re, time
from fit.Parse import Parse
from fit.Fixture import Fixture
from fit.ColumnFixture import ColumnFixture
from fit.TypeAdapter import adapterOnType, adapterOnField, adapterOnMethod

class RowFixture(ColumnFixture):
    """
    """
    results = []
    missing = []
    surplus = []

    #public void doRows(Parse rows):
    def doRows(self,rows):
        try:
            self.bind(rows.parts)
            self.missing = []
            self.surplus = []
            self.results = self.query()
            self.match(self.listOfRows(rows.more),
                       self.results,
                       0)
            last = rows.last()
            last.more = self.buildRows(self.surplus)
            self.markRows(last.more, "surplus")
            self.markList(self.missing, "missing")
        except Exception, e:
            self.exception(rows.leaf(), e)

    #abstract public Object[] query() throws Exception;
    def query(self):                             ## get rows to be compared
        pass

    #abstract public Class getTargetClass();     ## get expected type of row
    def getTargetClass(self):
        pass

    #void match(List expected, List computed, int col):
    def match(self, expected, computed, col):
        if col >= len(self.columnBindings):
            self.check(expected, computed)
        elif self.columnBindings[col] == None:
            match (expected, computed, col + 1)
        else:
            eMap = self.eSort(expected, col)
            cMap = self.cSort(computed, col)
            keys = self.union(eMap.keys(),cMap.keys())
            for key in keys:
                eList = eMap.get(key,None)
                cList = cMap.get(key,None)
                if not eList:
                    self.surplus.extend(cList)
                elif not cList:
                    self.missing.extend(eList)
                elif len(eList)==1 and len(cList)==1:
                    self.check(eList, cList)
                else:
                    self.match(eList, cList, col+1)
            
    #List list (Parse rows):
    #List list (Object[] rows):
    def listOfRows(self, rows):
        result = []
        while rows:
            result.append(rows)
            rows = rows.more
        return result

    #Map eSort(List list, int col):
    def eSort(self,list,col):
        a = self.columnBindings[col]
        result = {}
        for row in list:
            cell = row.parts.at(col)
            try:
                key = a.parse(cell.text())
                self.bin(result, key, row)
            except Exception, e:
                self.exception(cell, e)
                # mark the rest of the row as ignored (i.e. grey it out)
                rest = cell.more
                while cell:
                    self.ignore(rest)
        return result
    
    #Map cSort(List list, int col):
    def cSort(self, list, col):
        a = self.columnBindings[col]
        result = {}
        for row in list:
            try:
                a.target = row
                key = a.get()
                self.bin(result, key, row)
            except Exception:
                ## surplus anything with bad keys, including None
                self.surplus.append(row)
        return result
    
    #void bin (Map map, Object key, Object row):
    def bin(self, map, key, row):
        if map.has_key(key):
            map[key].append(row)
        else:
            map[key] = [row]
        
    #Set union (Set a, Set b):
    def union(self, a, b):
        result = a
        for i in b:
            if i not in result:
                result.append(i)
        return result
    
    #void check (List eList, List cList):
    def check (self, eList, cList):
        # called either when both sizes are one, or we've run out of columns
        # to compare. The first set of tests stops the recursion.
        if not eList:
            self.surplus.extend(cList)
            return
        if not cList:
            self.missing.extend(eList)
            return
        # There is at least one in each list. Process the first one,
        # and then recurse on the shorter lists
        row = eList.pop(0)
        cell = row.parts
        obj = cList.pop(0)
        for a in self.columnBindings:
            a.target = obj
            if a != None:
                a.target = obj
            Fixture.check(self, cell, a)
            cell = cell.more
        self.check(eList, cList)

    #void mark(Parse rows, String message):
    def markRows(self, rows, message):
        annotation = self.label(message)
        while rows:
            self.wrong(rows.parts)
            rows.parts.addToBody(annotation)
            rows = rows.more

    #void mark(Iterator rows, String message):
    def markList(self, rows, message):
        annotation = self.label(message)
        for row in rows:
            self.wrong(row.parts)
            row.parts.addToBody(annotation)

    #Parse buildRows(Object[] rows):
    def buildRows(self, rows):
        next = root = Parse(None, None, None, None)
        for row in rows:
            next.more = Parse(tag="tr",body=None,
                              parts=self.buildCells(row),more=None)
            next = next.more
        return root.more

    #Parse buildCells(Object row):
    def buildCells(self, row):
        if not row:
            nil = Parse(tag="td",body="None",parts=None,more=None)
            nil.addToTag(" colspan="+str(len(self.columnBindings)))
            return nil
        next = root = Parse(None, None, None, None)
        for i in range(len(self.columnBindings)):
            next.more = Parse(tag="td",body="&nbsp;",parts=None,more=None)
            next = next.more
            a = self.columnBindings[i]
            if not a:
                self.ignore(next)
            else:
                try:
                    a.target = row
                    next.body = self.gray(self.escape(a.toString(a.get())))
                except Exception, e:
                    self.exception(next, e)
        return root.more
