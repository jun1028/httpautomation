"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

# 2003/07/23 Add two special purpose type adapters: CommentAdapter and
#           UnimplementedMethodAdapter
# 2009/04/24 modify adapterCommon:modify,elif name[0] == "?"->elif name[0] == "?" or name[0] == "!"

import string, re
from types import *

class NoTypeInfoException(Exception):
    pass

class NoSuchMethodOrFieldException(Exception):
    pass

class UnsupportedTypeException(Exception):
    pass

class MissingAttributeException(Exception):
    pass


## Factory ##################################

def adapterOnType(fixture, typeName, targetClass = None):
    """
    Return a dummy adapter which can parse a string to this type
    """
    a = adapterForStringTypeName(typeName)
    a.init(fixture)
    return a

def adapterCommon(fixture, name, fieldOrMethod, targetClass = None):
    """
    Return an adapter adapting this field of fixture's class (or
    targetclass) to the fit TypeAdapter interface (in the context of
    fixture).
    """
    theClass = targetClass or getattr(fixture, "__class__")
    realName = name
    if name == "":
        a = CommentAdapter()
        obj = None
    elif name[0] == "?" or name[0] == "!":
        a = UnimplementedMethodAdapter()
        obj = None
    else:
        typeName = theClass._typeDict.get(name)
        if typeName == None:
            raise NoTypeInfoException, name
        #print theClass._typeDict
        realName = theClass._typeDict.get("%s.renameTo" %(name,)) or name
        obj = getattr(theClass, realName, None)
        if obj == None:
            raise NoSuchMethodOrFieldException, realName
        if type(typeName) != type(""):
            a = typeName()
        else:
            a = adapterForStringTypeName(typeName)
    if a == None:
        raise UnsupportedTypeException, typeName
    if fieldOrMethod == "Field":
        a.field = realName
    else:
        a.method = obj
    a.targetClass = theClass
    a.init(fixture, name, realName)
    a.target = fixture
    return a

def adapterOnField(fixture, fieldName, targetClass = None):
    """
    Return an adapter adapting this field of fixture's class (or
    targetclass) to the fit TypeAdapter interface (in the context of
    fixture).
    """

    a = adapterCommon(fixture, fieldName, "Field", targetClass)    
    return a
        
def adapterOnMethod(fixture, methodName, targetClass = None):
    """
    Return an adapter adapting this unbound method to the fit
    TypeAdapter interface (in the context of fixture).
    """

    a = adapterCommon(fixture, methodName, "Method", targetClass)
    return a

def adapterForStringTypeName(typeName):
    if typeName == "String": return StringAdapter()
    if typeName == "Int": return IntAdapter()
    if typeName == "Long": return LongAdapter()
    if typeName == "Float": return FloatAdapter()
    if typeName == "Complex": return ComplexAdapter()
    if typeName == "Boolean": return BooleanAdapter()
    if typeName == "List": return ListAdapter()
    if typeName == "Tuple": return TupleAdapter()
    return StringAdapter()
        
## util class ####################################

class TypeAdapter(object):
    """
    """
    name    = ""   # Name used by test tables
    fixture = None
    type    = None
    target  = None
    field   = None # name (one or the other, not both)
    method  = None # actual function object
    targetClass = None

    def init(self, fixture, name = None, realName = None):
        self.fixture = fixture
        self.name = name
        self.realName = realName

    def get(self):
        if self.field: return getattr(self.target,self.field)
        elif self.method: return self.invoke()
        else: return None

    def set(self,value):
        if self.field:
            setattr(self.target,self.field,value)

    def invoke(self):
        return self.method(self.target)
    
    def parse(self,s):
        return self.fixture.parse(s, self.type)
    
    def equals(self, a, b):
        return a == b

    def toString(self, o):
        return re.sub(r"^'(.+)'$",r"\1",repr(o))

    def shouldIgnore(self, text):
        """returns  0 - continue with normal path
                    1 - leave background white and continue and go to next cell
                    2 - ignore cell (turn background grey and count it)
        """
        return 0

## Subclasses ##############################
# these are forgiving parsers, which may or may not be what we want

class StringAdapter(TypeAdapter):
    def __init__(self):
        self.type = StringType
        
    def parse(self,s):
        return s.strip()

    def toString(self, s):
        return s.strip()

class IntAdapter(TypeAdapter):
    def __init__(self):
        self.type = IntType
        
    def parse(self,s):
        return int(s)

    def toString(self, s):
        return str(s)

class LongAdapter(TypeAdapter):
    def __init__(self):
        self.type = LongType
        
    def parse(self,s):
        return long(s)

class FloatAdapter(TypeAdapter):
    def __init__(self):
        self.type = FloatType

    def init(self, fixture, name, realName):
        super(FloatAdapter, self)
        attributeKey = "%s.precision" % (name,)
        self.precision = .00001
        precision = self.targetClass._typeDict.get(attributeKey)
        if type(precision) == type(1):
            self.precision = pow(0.1, precision)

    def parse(self,s):
        return float(s)

    def equals(self, a, b):
        return abs(a - b) < self.precision
    
class ComplexAdapter(TypeAdapter):
    def __init__(self):
        self.type = ComplexType
        
    def parse(self,s):
        return complex(s)

class BooleanAdapter(TypeAdapter):
    def __init__(self):
        self.type = IntType # should change to BooleanType in Python 2.3
        
    def parse(self, s):
        value = s.strip()
        if value.lower() in ("true","yes", "1"): return 1
        else: return 0

    def strToBool(self, value):
        if value.lower() in ("false", "no", "0"): return 0
        else: return 1

    def equals(self, a, b):
        if type(a) == type(""):
            a = self.strToBool(a)
        if a not in (0, 1):
            a = 0
        if type(b) == type(""):
            b = self.strToBool(b)
        if b not in (0, 1):
            b = 0
        return a == b

class ListAdapter(TypeAdapter):
    def __init__(self):
        self.type = ListType

    def init(self, fixture, name, realName):
        super(ListAdapter, self)
        attributeKey = "%s.scalarType" % (name,)
        typeName = self.targetClass._typeDict.get(attributeKey)
        if typeName == None:
            raise MissingAttributeException, attributeKey
        self.scalarAdapter = adapterForStringTypeName(typeName)
        if self.scalarAdapter == None:
            raise UnsupportedTypeException, typeName
        self.scalarAdapter.field = self.field
        self.scalarAdapter.method = self.method
        self.scalarAdapter.init(fixture, name, realName)
        self.scalarAdapter.target = fixture

    def parse(self, text):
        return map(lambda x: self.scalarAdapter.parse(x.strip()), text.split(","))
   
    def toString(self, listIn):
        list1 = map(lambda x: self.scalarAdapter.toString(x), listIn)
        return ", ".join(list1)

class TupleAdapter(ListAdapter):    
    def __init__(self, scalarTypeName):
        self.type = TupleType

    def parse(self, text):
        return tuple(map(lambda x: self.scalarAdapter.parse(x.strip()), text.split(",")))

class CommentAdapter(StringAdapter):
    def shouldIgnore(self, text):
        return 1

class UnimplementedMethodAdapter(StringAdapter):
    def shouldIgnore(self, text):
        if text == "":
            return 1
        else:
            return 2
