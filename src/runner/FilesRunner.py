# -*- coding: UTF-8 -*-
'''
@author: water
测试当前目录&子目录下所有的测试用例文件
'''

import os
import sys

from log.Log import Log
from runner import ExcelTestDriver


def getFiles(foldername, parentdir = None, filepaths = []):
    '''
            获取当前目录&子目录下所有的文件名
    '''
    Log.debug('start: FilesRunner getFiles')
    if parentdir:
        curpath = os.path.join(parentdir, foldername)
    else:
        curpath = foldername
    if os.path.isdir(curpath):
        #当前目录下所有的文件或文件夹
        files = os.listdir(curpath)
        for filename in files:
            getFiles(filename, curpath, filepaths) 
    else:
        filepaths.append(curpath) 
    Log.debug('end: FilesRunner getFiles')
    return  filepaths

if __name__ == '__main__':
    foldername = sys.argv[1]
    files = getFiles(foldername)
    for filename in files:
        sys.argv[1] = filename
        ExcelTestDriver(sys.argv).run()
