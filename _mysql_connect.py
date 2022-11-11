import pymysql
from functools import wraps

# def drop_database(new_db):
#     query = "DROP DATABASE " + str(new_db)
#     return query
#
#
# def creation_database(new_db):
#     query = "CREATE DATABASE IF NOT EXISTS " + str(new_db)
#     return query


class MysqlConnect(object):

    def __init__(self, usr, pwd, host, db, port):
        self.__usr = usr
        self.__pwd = pwd
        self.__host = host
        self.dbname = db
        self.__port = int(port)
        self.db = None
        self.__cursor = None
        self.connect()

    def connect(self):
        try:
            self.db = pymysql.connect(host=self.__host, user=self.__usr, passwd=self.__pwd, db=self.dbname, port=self.__port)
            self.__cursor = self.db.cursor()
            if self.db.open:
                return 0
            else:
                return 1
        except pymysql.OperationalError:
            return 1

    def disconnect(self):
        self.db.close()

    def _reconnect(func):
        @wraps(func)
        def rec(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return (result)
            except pymysql.err.OperationalError as e:
                try:
                    if e[0] == 2013:
                        self.connect()
                        result = func(self, *args, **kwargs)
                        return result
                except TypeError:
                    print(e)
        return rec

    @_reconnect
    def fetchall(self, sql):
        try:
            self.__cursor.execute(sql)
            res = self.__cursor.fetchall()
            return res
        except Exception as ex:
            print(ex)

    @_reconnect
    def fetchone(self, sql):
        try:
            self.__cursor.execute(sql)
            res = self.__cursor.fetchone()
            return res
        except Exception as ex:
            return None

    @_reconnect
    def execute(self, sql):
        self.__cursor.execute(sql)
        self.db.commit()

    @_reconnect
    def last_id(self):
        return self.__cursor.lastrowid