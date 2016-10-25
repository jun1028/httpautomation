"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

import string, re, time
from types import *
from fit.Parse import Parse, ParseException
from fit.Fixture import Fixture
from fit.TypeAdapter import adapterOnType, adapterOnField, adapterOnMethod

class NoSuchMethodException(Exception):
    pass

class ActionFixture(Fixture):
    """
    """
    cells = None
    actor = None
    empty = []

    ## Traversal ################################

    #public void doCells(Parse cells) {
    def doCells(self, cells):
        self.cells = cells
        try:
            # calls instance method - import to look up class method
            # (and call with empty instance ?) as java does ?
            # add a _ to these to avoid hiding Fixture.check
            getattr(self,cells.text()+'_')()
        except Exception, e:
            self.exception(cells, e)
        
    ## Actions ##################################

    #public void start() throws Exception {
    def start_(self):
        #how does this work in java ?
        #self.actor = eval(self.cells.more.text()+'()')
        path = self.cells.more.text()
        clas = path.split('.')[-1]
        exec 'import ' + path
        exec "ActionFixture.actor = " + path + "." + clas + "()"
#        exec 'self.__class__.actor = '+path+'.'+clas+'()'

    #public void enter() throws Exception {
    def enter_(self):
        methodName = self.camel(self.cells.more.text())
        adapter = adapterOnMethod(self.actor, methodName)
        parameterString = self.cells.more.more.text()
        args = adapter.parse(parameterString)
        adapter.method(self.actor, args)

    #public void press() throws Exception {
    def press_(self):
        self.method(0)(self.actor)

    #public void check() throws Exception {
    def check_(self):
        text = self.camel(self.cells.more.text())
        adapter = adapterOnMethod(self.actor, text)
        Fixture.check(self, self.cells.more.more, adapter)

    ## Utility ##################################

    #Method method(int args) throws NoSuchMethodException {
    # !!! The bizarre test at the front is because the Java
    #     version suddenly sprouted two methods named method,
    #     with incompatible arguement lists. I hope this is
    #     never overridden!
    def method(self, arg1, arg2 = None):
        if arg2 == None:
            test = self.camel(self.cells.more.text())
            numArgs = arg1
        else:
            test = arg1
            numArgs = arg2
        theClass = self.actor.__class__
        method = getattr(theClass, test, None)
        if method == None or \
           not callable(method) or \
           method.im_func.func_code.co_argcount != 1+numArgs:
            raise NoSuchMethodException
        return method    