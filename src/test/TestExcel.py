'''

@author: Water
'''
import util.excel
if __name__ == '__main__':
    test = util.excel.ExcelAppRD()
    test.open('test.xls')
    sheet = test.getShByIndex(0)
    for rx in range(sheet.nrows):
        print sheet.row(rx)
    print test.getCellStrValue(0, 3, sheet),
    print test.getCellStrValue(0, 0, sheet)
    print test.curSheet.name
    print test.getRow(0)