'''

@author: water.zhang
'''
from util.ConvertExcelToHtml import ConvertExcelToHtml

if __name__ == '__main__':
    test = ConvertExcelToHtml()
    #test.convertExcelToHtml('')
    test.convertExcelToHtml('sample.xls')