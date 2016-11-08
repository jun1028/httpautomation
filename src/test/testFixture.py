# -*- coding: UTF-8 -*-
'''

@author: Water
'''
fixturePath = ''
if fixturePath == '':  # if have not fixture row, use default fixture
    fixturePath = 'fixture.TempleteFixture'
_CLASSNAME = fixturePath.split('.')[-1]
# fix for illegal Java trick in AllFiles. Frankly, I like it!
i = fixturePath.split('$')
if len(i) == 1:
    exec 'import '+ fixturePath
    #test class method
    exec 'fixture = ' + fixturePath + '.' + _CLASSNAME + '()' 
else:
    exec "import %s" % (i[0],)
    exec "fixture = %s.%s()" % (i[0], i[1])
print fixture._CLASSNAME