import sqlite3
import math
import time


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getLogPass(self, input_log):
        sql = f'''SELECT _user, _pass FROM users WHERE _user = "{input_log}"'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return [dict(i) for i in res]
        except sqlite3.Error as e:
            print("Ошибка чтения из БД" + str(e))
        return []

    def fromReports(self):
        sql = '''SELECT * FROM reports'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return {}

    def addTask(self, task_name,  report_name, label1, label2, isactive):
        try:
            t_create = math.floor(time.time())
            self.__cur.execute("INSERT INTO actions VALUES(NULL,?,?,?,?,?,?)", (task_name,  report_name, t_create, label1, label2, isactive))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+str(e))
            return False
        return True

    def fromActions(self):
        sql = '''SELECT * FROM actions'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return {}
