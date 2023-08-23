import sqlite3


class FDataBase:
    def __init__(self, db):
        print(db)
        self.__db = db
        print(db.cursor())
        self.__cur = db.cursor()
    def getLogPass(self, input_log):
        sql = f'''SELECT _user, _pass FROM users WHERE _user = "{input_log}"'''
        #print(sql)
        # try:
        self.__cur.execute(sql)
        res = self.__cur.fetchall()
        if res: return [dict(i) for i in res]
        # except:
        #
        #     print("Ошибка чтения из БД")
        return []
