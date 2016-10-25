"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General License version 2 or later.
"""

import string, re, unittest
from Parse import Parse, ParseException
from Fixture import Fixture
from ColumnFixture import ColumnFixture
from TypeAdapter import adapterOnType, adapterOnField, adapterOnMethod

class FrameworkTest(unittest.TestCase):
    def testParsing(self):
        tags = ("table",)
        p = Parse("leader<Table foo=2>body</table>trailer", tags)
        self.assertEquals("leader", p.leader)
        self.assertEquals("<Table foo=2>", p.tag)
        self.assertEquals("body", p.body)
        self.assertEquals("trailer", p.trailer)
    
    def testRecursing(self):
        p = Parse("leader<table><TR><Td>body</tD></TR></table>trailer")
        self.assertEquals(None, p.body)
        self.assertEquals(None, p.parts.body)
        self.assertEquals("body", p.parts.parts.body)
    
    def testIterating(self):
        p = Parse("leader<table><tr><td>one</td><td>two</td><td>three</td></tr></table>trailer")
        self.assertEquals("one", p.parts.parts.body)
        self.assertEquals("two", p.parts.parts.more.body)
        self.assertEquals("three", p.parts.parts.more.more.body)
    
    def testIndexing(self):
        p = Parse("leader<table><tr><td>one</td><td>two</td><td>three</td></tr><tr><td>four</td></tr></table>trailer")
        self.assertEquals("one", p.at(0,0,0).body)
        self.assertEquals("two", p.at(0,0,1).body)
        self.assertEquals("three", p.at(0,0,2).body)
        self.assertEquals("three", p.at(0,0,3).body)
        self.assertEquals("three", p.at(0,0,4).body)
        self.assertEquals("four", p.at(0,1,0).body)
        self.assertEquals("four", p.at(0,1,1).body)
        self.assertEquals("four", p.at(0,2,0).body)
        self.assertEquals(1, p.size())
        self.assertEquals(2, p.parts.size())
        self.assertEquals(3, p.parts.parts.size())
        self.assertEquals("one", p.leaf().body)
        self.assertEquals("four", p.parts.last().leaf().body)

    def testParseException(self):
        try:
            p = Parse("leader<table><tr><th>one</th><th>two</th><th>three</th></tr><tr><td>four</td></tr></table>trailer")
        except ParseException, e:
            self.assertEquals(17, e.offset)
            self.assertEquals("Can't find tag: td", e.message)
            return
        self.fail("expected exception not thrown")

    def testText(self):
        tags =("td",)
        p = Parse("<td>a&lt;b</td>", tags)
        self.assertEquals("a&lt;b", p.body)
        self.assertEquals("a<b", p.text())
        p = Parse("<td>\ta&gt;b&nbsp;&amp;&nbsp;b>c &&&nbsp;</td>", tags)
        self.assertEquals("a>b & b>c &&", p.text())
        p = Parse("<td>\ta&gt;b&nbsp;&amp;&nbsp;b>c &&nbsp;</td>", tags)
        self.assertEquals("a>b & b>c &", p.text())
        p = Parse("<TD><P><FONT FACE=\"Arial\" SIZE=2>GroupTestFixture</FONT></TD>", tags)
        self.assertEquals("GroupTestFixture",p.text())

    def testUnescape(self):
        self.assertEquals("a<b", Parse().unescape("a&lt;b"))
        self.assertEquals("a>b & b>c &&", Parse().unescape("a&gt;b&nbsp;&amp;&nbsp;b>c &&"))
        self.assertEquals("&amp;&amp;", Parse().unescape("&amp;amp;&amp;amp;"))
        self.assertEquals("a>b & b>c &&", Parse().unescape("a&gt;b&nbsp;&amp;&nbsp;b>c &&"))

    def testUnformat(self):
        self.assertEquals("ab",Parse().unformat("<font size=+1>a</font>b"))
        self.assertEquals("ab",Parse().unformat("a<font size=+1>b</font>"))
        self.assertEquals("a<b",Parse().unformat("a<b"))

    def testTypeAdapter(self):
        f = TestFixture()
        a = adapterOnField(f, 'sampleInt')
        a.set(a.parse("123456"))
        self.assertEquals(123456, f.sampleInt)
        self.assertEquals("-234567", str(a.parse("-234567")))
        a = adapterOnMethod(f, "pi")
# we do not currently support creating an adapter from a method declaration
#        a = adapterOnMethod(f, f.__class__.pi)
        self.assert_(abs(3.14159 - a.invoke()) < 0.00001)
        self.assertEquals(3.14159862, a.invoke())
        a = adapterOnField(f, 'sampleString')
        a.set(a.parse("xyzzy"))
        self.assertEquals('xyzzy', f.sampleString)
        a = adapterOnField(f, 'sampleFloat')
        a.set(a.parse("6.02e23"))
        # not sure what the 1e17 is supposed to be here. If it's the epsilon,
        #  the Python version of xUnit does not support it. We can get a
        #  similar effect by inserting a .precision into _typeDict.
        self.assertEquals(6.02e23, f.sampleFloat) #, 1e17
        # the remaining tests in the September 2002 version were commented
        #  out because the type adapter strategy didn't support lists. The
        #  current strategy does.

    def testTypeAdapter2(self):
        # only the phrases that aren't included in the first test
        f = TestFixture()
        a = adapterOnField(f, "sampleInteger")
        a.set(a.parse("54321"))
        self.assertEquals("54321", str(f.sampleInteger))

# This phrase will never work on Python, since Python does not have a
#  single character type.
##        a = adapterOnField(f, "ch")
##        a.set(a.parse("abc"))
##        self.assertEquals('a', f.ch)
        
        a = adapterOnField(f, "name")
        a.set(a.parse("xyzzy"))
        self.assertEquals("xyzzy", f.name)
        
        a = adapterOnField(f, "sampleFloat")
        a.set(a.parse("6.02e23"))
        self.assertEquals(6.02e23, f.sampleFloat, 1e17);
                          
        a = adapterOnField(f, "sampleArray")
        a.set(a.parse("1,2,3"))
        self.assertEquals(1, f.sampleArray[0])
        self.assertEquals(2, f.sampleArray[1])
        self.assertEquals(3, f.sampleArray[2])
        self.assertEquals("1, 2, 3", a.toString(f.sampleArray))
        self.assertEquals(a.equals([1,2,3], f.sampleArray), 1)

# we do not currently have a generic date adapter.
#        a = TypeAdapterOnField(f, "sampleDate")
#        date = Date(49,4,26)
#        a.set(a.parse(DateFormat.getDateInstance().format(date)))
#        self.assertEquals(date, f.sampleDate)
                          
        a = adapterOnField(f, "sampleByte")
        a.set(a.parse("123"))
        self.assertEquals(123, f.sampleByte)
        a = adapterOnField(f, "sampleShort")
        a.set(a.parse("12345"))
        self.assertEquals(12345, f.sampleShort)
    

#     def testScientificDouble(self):
#         Double pi = new Double(3.141592865)
#         self.assertEquals(ScientificDouble.valueOf("3.14"), pi)
#         self.assertEquals(ScientificDouble.valueOf("3.141"), pi)
#         self.assertEquals(ScientificDouble.valueOf("3.1415"), pi)
#         self.assertEquals(ScientificDouble.valueOf("3.14159"), pi)
#         self.assertEquals(ScientificDouble.valueOf("3.141592865"), pi)
#         self.assertTrue(!ScientificDouble.valueOf("3.140").equals(pi))
#         self.assertTrue(!ScientificDouble.valueOf("3.144").equals(pi))
#         self.assertTrue(!ScientificDouble.valueOf("3.1414").equals(pi))
#         self.assertTrue(!ScientificDouble.valueOf("3.141592863").equals(pi))
#         Float av = new Float(6.02e23)
#         self.assertEquals(ScientificDouble.valueOf("6.0e23"), av)

    def testEscape(self):
        junk = "!@#$%^*()_-+={|[]\\:\";',./?`"
        self.assertEquals(junk, Fixture().escape(junk))
        self.assertEquals("", Fixture().escape(""))
        self.assertEquals("&lt;", Fixture().escape("<"))
        self.assertEquals("&lt;&lt;", Fixture().escape("<<"))
        self.assertEquals("x&lt;", Fixture().escape("x<"))
        self.assertEquals("&amp;", Fixture().escape("&"))
        self.assertEquals("&lt;&amp;&lt;", Fixture().escape("<&<"))
        self.assertEquals("&amp;&lt;&amp;", Fixture().escape("&<&"))
        self.assertEquals("a &lt; b &amp;&amp; c &lt; d", Fixture().escape("a < b && c < d"))

    def testRuns(self):
        self.run("arithmetic", 39, 9, 0, 1)
#        self.run("arithmetic", 37, 10, 0, 2) # see comments for differences
        self.run("CalculatorExample", 75, 8, 0, 1)
#        self.run("CalculatorExample", 75, 9, 0, 0) # floating divide by zero
        self.run("MusicExample", 95, 0, 0, 0)

    def run(self, file, right, wrong, ignores, exceptions):
        input = self.read("Documents/"+file+".html")
        fixture = Fixture()
        if input.find("<wiki>") != -1:
            tables = Parse(input, ("wiki", "table", "tr", "td"))
            fixture.doTables(tables.parts)
        else:
            tables = Parse(input, ("table", "tr", "td"))
            fixture.doTables(tables)
        output = open("Reports/"+file+".html", "wt")
        output.write(str(tables))
        output.close()
        self.assertEquals(right, fixture.counts.right, file+" right")
        self.assertEquals(wrong, fixture.counts.wrong, file+" wrong")
        self.assertEquals(ignores, fixture.counts.ignores, file+" ignores")
        self.assertEquals(exceptions, fixture.counts.exceptions, file+" exceptions")

    def read(self, inputName):
        fileObj = open(inputName, "rt")
        chars = fileObj.read()
        fileObj.close()
        return chars

class TestFixture(ColumnFixture): ## used in testTypeAdapter
     _typeDict = {"sampleByte": "Int",
                  "sampleShort": "Int", 
                  "sampleInt": "Int",
                  "sampleInteger": "Int",
                  "sampleFloat": "Float",
                  "pi": "Float",
                  "ch": "String",
                  "name": "String",
                  "sampleArray": "List",
                  "sampleArray.scalarType": "Int",
                  "sampleString": "String",
                  "sampleList": "List",
                  "sampleList.scalarType": "Int",
                  "sampleDate": "String",
                 }
     sampleByte = 0
     sampleShort = 0
     sampleInt = 0
     sampleInteger = 0
     sampleFloat = 0.0
     def pi(self): return 3.14159862
     ch = ""
     name = ""
     sampleArray = []
     sampleString = ''
     sampleList = []
     sampleDate = ''

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FrameworkTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
