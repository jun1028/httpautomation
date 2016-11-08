"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

import string, re, time, sys, traceback
from log.Log import Log

class Counts:
    def __init__(self):
        self.right = 0
        self.wrong = 0
        self.ignores = 0
        self.exceptions = 0

    def toString(self):
        #toString("%s right, %s wrong, %s ignored, %s exceptions" )
        return ("%s pass, %s fail, %s ignored, %s exceptions" %
                (self.right, self.wrong, self.ignores, self.exceptions))

    def tally(self, source):
        self.right += source.right
        self.wrong += source.wrong
        self.ignores += source.ignores
        self.exceptions += source.exceptions

    def __str__(self):
        return self.toString()

class RunTime:
    def __init__(self):
        self.start = time.time()
        self.elapsed = 0.0

    def __str__(self):
        return self.toString()

    def toString(self):
        self.elapsed = time.time() - self.start
        if self.elapsed > 600:
            hours = self.d(3600)
            minutes = self.d(60)
            seconds = self.d(1)
            return "%s:%02s:%02s" % (hours, minutes, seconds)
        else:
            minutes = self.d(60)
            seconds = self.d(1)
            hundredths = self.d(.01)
            return "%s:%02s.%02s" % (minutes, seconds, hundredths)

    def d(self, scale):
        report = int(self.elapsed / scale)
        self.elapsed -= report * scale
        return report

class Fixture:
    """
    """
    
    def __init__(self):
        self.counts = Counts()
        self.summary = {}
    
    ## Traversal ##########################
                
    #public void doTables(Parse tables, str expandColumnsTag) {
    #@param expandColumnsTag:   expand column tag, like colspan = 23      
    def doTables(self,tables, expandColumnsTag = None) :
        self.summary["run date"] = time.ctime(time.time())
        self.summary["run elapsed time"] = RunTime()
        while tables:
            try:
                heading = tables.at(0,0,0)
                if expandColumnsTag is not None:
                    tempTuple = expandColumnsTag.split('=')
                    heading.modifyTagValue(tempTuple[0], tempTuple[1])
            except BaseException, e:
                Log.exception(e)                 
            if heading:
                try:
                    path = heading.text()
                    #path = re.sub(r'^fit\.','',path) #try to cure the fits of madness
                    _CLASSNAME = path.split('.')[-1]
                    # fix for illegal Java trick in AllFiles. Frankly, I like it!
                    i = path.split('$')
                    if len(i) == 1:
                        exec 'import '+path
                        #test class method
                        exec 'fixture = '+path+'.'+_CLASSNAME+'()' 
                    else:
                        exec "import %s" % (i[0],)
                        exec "fixture = %s.%s()" % (i[0], i[1])
                    fixture.counts = self.counts
                    fixture.summary = self.summary
                    fixture.doTable(tables, expandColumnsTag)
                except Exception, e:
                    self.exception(heading, e)
            tables = tables.more
        try:
            delattr(self, 'rowspan')
        except:
            pass
            
    #public void doTable(Parse table, str expandColumnsTag) {
    def doTable(self,table, expandColumnsTag = None):
        if expandColumnsTag != None:
            self.doRows(table.parts.more, expandColumnsTag)
        else:
            self.doRows(table.parts.more)
    
    #public void doRows(Parse rows) {
    def doRows(self, rows) :
        while rows:
            more = rows.more
            self.doRow(rows)
            rows = more

    #public void doRow(Parse row) {
    def doRow(self, row) :
        self.doCells(row.parts)
    
    #public void doCells(Parse cells) {
    def doCells(self, cells) :
        i = 0
        while cells:
            try:
                self.doCell(cells, i)
                i = i + 1
            except Exception, e:
                self.exception(cells, e)
            cells=cells.more
        
    #public void doCell(Parse cell, int columnNumber) {
    def doCell(self, cell, columnNumber) :
        self.ignore(cell)

    ## Annotation ##############################/

    #public static void right (Parse cell) {
    def right (self, cell, actual=None) :
        cell.addToTag(" bgcolor=\"#cfffcf\"")
        self.counts.right += 1
        if actual != None:
            cell.addToBody(self.greenlabel("expected") + "<hr>" + \
                           self.escape(actual) + self.greenlabel("actual"))
    
    #public static void output (Parse cell) {
    def output (self, cell, actual=None) :
        cell.addToTag(" bgcolor=\"#cfffcf\"")
        self.counts.right += 1
        cell.overrideToBody(actual)

    #public static void wrong (Parse cell) {
    #public static void wrong (Parse cell, String actual) {
    def wrong (self, cell, actual=None) :
        cell.addToTag(" bgcolor=\"#ffcfcf\"")
        self.counts.wrong += 1
        if actual != None:
            actual = self.label("expected") + "<hr>" + \
                           self.escape(actual) + self.label("actual")         
            cell.addToBody("<font size=2.0pt>%s</font>" % actual)
    
    #public static void ignore (Parse cell) {
    def ignore (self, cell) :
        cell.addToTag(" bgcolor=\"#efefef\"")        
    
    #public static void ignore (Parse cell) {
    def ignoreTest (self, cell) :
        cell.addToTag(" bgcolor=\"#efefef\"")
        cell.addToBody("Test case ignored!")
        self.counts.ignores += 1

    #public static void exception (Parse cell, Exception exception) {
    def exception(self, cell, exception) :
        type, val, tb = sys.exc_info()
        err = string.join(traceback.format_exception(type,val,tb),'')
        cell.addToBody("<hr><pre><font size=-2>%s</font></pre>" % err)
        cell.addToTag(" bgcolor=\"#ffffcf\"")
        self.counts.exceptions += 1
    
    ## Utility ##################################

    #public static String counts() {
    # !!! duplication of function and field name!!!
    # !!! should use str(self.counts) instead of this.
    def _counts(self) :
        return self.counts.toString()

    #static String label (String string) {
    def label (self,string) :
        return " <font size=-1 color=#c08080><i>%s</i></font>" % string
    
    def gray (self,string) :
        return " <font color=#808080>%s</font>" % string

    def greenlabel(self,string) :
        return " <font size=-1 color=#80c080><i>%s</i></font>" % string

    #static String escape (String string) {
    #static String escape (String string, char from, String to) {
    def escape (self, thestring, old=None, new=None) :
        if old==None:
            return self.escape(self.escape(thestring,'&',"&amp;"),'<',"&lt;")
        else:
            #return thestring.replace(old,new)
            return str(thestring).replace(old,new)

    # CamelCase routine - builds standardized field and method names.
    # Capitalize the first letter after a space, and then remove the space
    #static String camel (String name) {
    def camel (self, name) :
        b = ''
        token = re.compile('\w+')
        match = token.search(name)
        if match: b += match.group()
        while 1:
            match = token.search(name,match.end())
            if match:
                t = match.group()
                b += t[0].upper() + t[1:]
            else: break
        return b
    
    #public Object parse (String s, Class type) throws Exception {
    # XXX needs to check for Date and Scientific Double specially.
    def parse (self, s, type):
        return s

    #void check(Parse cell, TypeAdapter a) {
    def check(self, cell, a):
        text = cell.text()
        if text == "" :
            try:
                cell.addToBody(self.gray(a.toString(a.get())))
            except Exception, e:
                cell.addToBody(self.gray("error"))
        elif a == None:
            self.ignore(cell)
        elif text == "error":
            try:
                result = a.invoke()
                self.wrong(cell, a.toString(result))
            except BaseException, e:
                print e
                self.right(cell)
        else:
            try:
                expected = a.parse(text)
                result = a.get()
                if a.equals(expected, result):
                    # !!! extra test here puts both out if repr() doesn't match
                    #     this means you can't let repr() default in most cases.
                    if repr(expected) != repr(result):
                        self.right(cell, a.toString(result))
                    else:
                        self.right(cell)
                else:
                    self.wrong(cell, a.toString(result))
            except Exception, e :
                self.exception(cell, e)

