import sqlite3


class Database:
    def __init__(self, db_path):
        self.__conn = sqlite3.connect(db_path)
        self.__cur = self.__conn.cursor()

    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM Us_user WHERE id = ? LIMIT 1", (user_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            
            return res
        except sqlite3.Error as ex:
            print("Ошибка получения данных: " + str(ex))
        
        return False    

    def getUserByEmail(self, email):
        try:
            self.__cur.execute("SELECT * FROM Us_user WHERE Email = ? LIMIT 1", (email,))
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            
            return res
        except sqlite3.Error as ex:
            print("Ошибка получения данных: " + str(ex))
        
        return False