"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""
#water.zhang
#       add overrideToBody(text) to  override dell's old data
#water.zhang
#       add modifyTagValue(tag, value) for modify special tag value,
#            NOT suitable for tag that include style ,like  style = 'background:black;height:56.1pt'
#       add getStyle()


import string, re
from log.Log import Log

class ParseException(Exception):
    def __init__(self, message, offset):
        self.message = message
        self.offset = offset
    def __str__(self):
        return '%s, %s' % (self.message,self.offset)

class Parse:
    """
    """
    leader  = ''
    tag     = ''
    body    = ''
    end     = ''
    trailer = ''
    more    = None
    parts   = None
    tags = ("table", "tr", "td")
    footnoteFiles = 0 # static class variable, not instance variable.

    # what's the cleanest way to map these to python ?
    #public Parse (String tag, String body, Parse parts, Parse more) {
    #public Parse (String text) throws ParseException {
    #public Parse (String text, String tags[]) throws ParseException {
    #public Parse (String text, String tags[], int level, int offset) throws ParseException {
    def __init__(self,
                 text=None,tags=tags,level=0,offset=0, # use either these
                 tag='',body='',parts=None,more=None): # or these
        if text == None:
            if tag == None: tag = ''
            if body == None: body = ''
            self.leader = "\n"
            self.tag = "<"+tag+">"
            self.body = body
            self.end = "</"+tag+">"
            self.trailer = ""
            self.parts = parts
            self.more = more
        else:
            lc = text.lower()
            startTag = lc.find("<"+tags[level])
            endTag = lc.find(">", startTag) + 1
            startEnd = lc.find("</"+tags[level], endTag)
            endEnd = lc.find(">", startEnd) + 1
            startMore = lc.find("<"+tags[level], endEnd)
            if (startTag<0 or endTag<0 or startEnd<0 or endEnd<0):
                raise ParseException(
                    "Can't find tag: " + tags[level], 
                    offset)

            self.leader = text[0:startTag]
            self.tag = text[startTag:endTag]
            self.body = text[endTag:startEnd]
            self.end = text[startEnd:endEnd]
            self.trailer = text[endEnd:]

            if (level+1 < len(tags)):
                self.parts = Parse(self.body, tags, level+1, offset+endTag)
                self.body = None

            if (startMore>=0):
                self.more = Parse(self.trailer, tags, level, offset+endEnd)
                self.trailer = None

    #public int size() {
    def size(self):
        if self.more:
            return self.more.size()+1
        else:
            return 1

    #public Parse last() {
    def last(self):
        if self.more:
            return self.more.last()
        else:
            return self

    #public Parse leaf() {
    def leaf(self):
        if self.parts:
            return self.parts.leaf()
        else:
            return self

    #public Parse at(int i) {
    #public Parse at(int i, int j) {
    #public Parse at(int i, int j, int k) {
    def at(self, i, j=None, k=None):
        if j == None and k == None:
            if (i==0 or not self.more):
                return self
            else:
                return self.more.at(i-1)
        elif k == None:
            return self.at(i).parts.at(j)
        else:
            return self.at(i,j).parts.at(k)

    #public String text() {
    def text(self):
        return self.unescape(self.unformat(self.body)).strip()

    #static String unformat(String s) {
    def unformat(self, s):
        #return re.sub('<.*?>','',s)
        i=0
        while 1:
            i = s.find('<',i)
            if i == -1: break
            j = s.find('>',i+1)
            if j >= 0:
                s = s[:i] + s[j+1:]
            else: break
        return s

    #static String unescape(String s) {
    def unescape(self,s):
        #return re.sub('&([^&]*?);',lambda x:self.replacement(x.group(1)),s)
        i=-1
        while 1:
            i = s.find('&',i+1)
            if i == -1: break
            j = s.find(';',i+1)
            if j >= 0:
                fromstring = s[i+1:j].lower()
                tostring = self.replacement(fromstring)
                if tostring:
                    s = s[:i] + tostring + s[j+1:]
        return s

    #static String replacement(String from) {
    def replacement(self,s):
        entities = {
            'lt':'<',
            'gt':'>',
            'amp':'&',
            'nbsp':' ',
            }
        if s in entities.keys(): return entities[s]
        else: return None

    #public void addToTag(String text) {
    def addToTag(self, text):
        self.tag = self.tag[:-1] + text + ">"

    #public void addToBody(String text) {
    def addToBody(self,text):
        self.body = self.body + text
    
    #override the old text
    def overrideToBody(self,text):
        self.body = text
    
    #modify some tag's value by tag
    def modifyTagValue(self, tag, value):
        tagTuple = self.tag.split(' ')
        oldTag = ''
        tag = tag.strip()
        for oldTag in tagTuple:
            if oldTag.find(tag) > -1:
                newTag =  tag + '=' + str(value)
                if oldTag.find('>') > -1:
                    self.tag = self.tag.replace(oldTag, newTag + '>')
                else:
                    self.tag = self.tag.replace(oldTag, newTag)
                break
    
    #get Style  form td tag
    def getStyle(self):
        result = ''
        try:
            place1 = self.tag.find('style')
            if place1 > -1:
                place2 = self.tag.find("'", place1 + 7) # get last "'" of the tag. style = '...'
                if place2 > -1:
                    result = self.tag[place1:place2 + 1]
        except BaseException, e:
            Log.exception(e)
        return result     
         
    #public void print(PrintWriter out) {
    def __str__(self):
        s = self.leader
        s += self.tag
        if self.parts:
            s += str(self.parts())
        else:
            s += self.body
        s += self.end
        if self.more:
            s += str(self.more)
        else:
            s += self.trailer
        return s

    # This assumes that the current directory is fit/, and that the
    # browser is set to one directory above fit/. This may not be true.

    def footnote(self):
        if Parse.footnoteFiles >= 25:
            return ["="]
        Parse.footnoteFiles += 1
        thisFootnote = Parse.footnoteFiles
        html = "footnotes/%s.html" % (thisFootnote,)
        file = open("Reports/" + html, "wt")
        file.write(str(self))
        file.close()
        return "<a href='%s'>[%s]</a>" % (html, thisFootnote)

    __call__ = __str__
