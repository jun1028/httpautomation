from fit.ColumnFixture import ColumnFixture
from util.Sum import Sum

class SumFixture(ColumnFixture):
    value1 = 0
    value2 = 0
    _typeDict = {"value1": "int",
                 "value2": "int",
                 "testSum":'str'}
    
    def __init__(self):
        self.TargetClass = Sum()
        
    def testSum(self):
        s = self.TargetClass.sum(self.value1, self.value2)
        return  s
    
if __name__ == '__main__' :
    test = SumFixture()
    print test.testSum()
