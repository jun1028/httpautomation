# -*- coding: UTF-8 -*-
'''

@author: Water
'''
import os
import logging
import LogSetting


class Log():

    _single = None
    _fileHdlr = None
    _logger = None
    _levelDict = {"debug": logging.DEBUG,
                  "info": logging.INFO,
                  "warn": logging.WARNING,
                  "error": logging.ERROR,
                  "critical": logging.CRITICAL
                  }

    # singleton
    def __init__(self):
        if Log._single:
            raise Log._single
        Log._single = self

    @staticmethod
    def getInstance():
        try:
            _single = Log()
        except Log, s:
            _single = s
        return  _single

    @staticmethod
    def getlog():
        try:
            if Log._logger is None:
                Log._logger = logging.getLogger('simple')
                if Log._fileHdlr is None:
                    if os.path.exists(LogSetting.LOG_FILE):
                        filename = LogSetting.LOG_FILE
                    else:
                        filename = 'log.log'
                    Log._fileHdlr = logging.FileHandler(\
                                            filename, LogSetting.LOG_FILEMODE)
                    formatter = logging.Formatter(\
                                '%(asctime)s %(levelname)s %(message)s')
                    Log._fileHdlr.setFormatter(formatter)
                    Log._logger.addHandler(Log._fileHdlr)
                    Log._logger.setLevel(Log._levelDict.get(LogSetting.LOG_LEVEL, logging.NOTSET))
        except BaseException as e:
            print e
        return Log._logger

    @staticmethod
    def info(msg):
        try:
            Log.getlog().info(msg)
        except:
            pass

    @staticmethod
    def debug(msg, comment=''):
        try:
            if comment:
                msg = str(msg) + ' ' + str(comment)
            Log.getlog().debug(str(msg))
        except:
            pass

    @staticmethod
    def debugvar(msg, var):
        try:
            Log.getlog().debug(str(msg) + str(var))
        except:
            pass

    @staticmethod
    def exception(msg):
        try:
            Log.getlog().exception(msg)
        except:
            pass

    @staticmethod
    def error(msg, msg1=''):
        try:
            Log.getlog().error(str(msg) + ',' + str(msg1))
        except:
            pass

    @staticmethod
    def close():
        try:
            if Log._fileHdlr is not None:
                Log._logger.removeHandler(Log._fileHdlr)
                Log._logger._fileHdlr.close()
            del Log._logger
        except:
            pass

#test
if __name__ == '__main__':
    Log.info('info')
    Log.debug('debug')
    Log.exception('excoeption')
    temp = Log.getInstance()
    log = temp.getlog()
    log.debug('debug test')
    log.info("WRITE TEST TO LOG")
    log.warn('dfdfdf')
    log.error('dfd')
    log.exception('dfdf')
    temp.close()

