# -*- coding: UTF-8 -*-
# package: util.DbUtils.db
'''

@author: water
'''
import MySQLdb
from log.Log import Log


class Singleton(object):  
    
    ''''' A python style singleton '''  
    def __new__(cls, *args, **kw):  
        if not hasattr(cls, '_instance'):  
            org = super(Singleton, cls)  
            cls._instance = org.__new__(cls, *args, **kw)  
        return cls._instance
    
class db(Singleton):
    
    CONTYPE_MYSQL  = 0
    CONTYPE_MSSQL  = 1
    CONTYPE_ORCALE = 2
    
    DEFAULTHOST       = 'localhost'
    DEFAULTUSER       = 'root'
    DEFAULTPWD        = 'root'
    DEFAULTDBNAME     = 'test1'
    DEFAULTDBNAMEPORT = 3306
    
    def __init__(self, host=DEFAULTHOST, user=DEFAULTUSER, passwd=DEFAULTPWD, database=DEFAULTDBNAME, port=DEFAULTDBNAMEPORT):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.port = port
        self.conn = None
        self.cur = None
    
    def conToDb(self, conType = None):   
            if not self.conn:
                if conType == self.CONTYPE_ORCALE:
                    pass
                elif conType == self.CONTYPE_MSSQL:
                    pass
                else:
                    self.con2mysql()
                
    
    def con2mysql(self):
        try:
            self.conn = MySQLdb.connect(self.host, self.user, self.passwd, self.database, self.port, charset='utf8')
            self.cur = self.conn.cursor()
        except MySQLdb.Error,e:
            print "Mysql connect failed! Error %d: %s" % (e.args[0], e.args[1])
            Log.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            
    def execute(self, sql):
        result = False
        try:
            result = self.cur.execute(sql)
            Log.debug("execute sql statement!", sql)
            print "execute sql success"
            result = True
        except Exception, e:
            print "Execute Fail!"
            Log.error("execute sql fail!", e)
        return result
    
    def commit(self):
        bresult = True
        try:
            self.conn.commit()
        except:
            bresult = False
        return bresult

    def query(self, sql):
        results = None
        try:
            if self.cur.execute(sql):
                results = self.cur.fetchall()
        except:
            Log.error("query fail!")
        return results
       
    def close(self):
        try:
            self.cur.close()
            self.conn.close()
            print "close db success!"
        except:
            Log.error("close fail!")
            print 'close db fail!'



class DataManagement():
    
    _CLASSNAME = 'DataManagement'
        
if __name__ == '__main__':
    db = db()
    db.conToDb()
    sql = "SELECT * FROM USERS"
    results  = db.query(sql)
    if results:
        for row in results:
            for i in range(0, len(row)):
                print row[i]
    db.close()