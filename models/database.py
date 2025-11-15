import pymysql
from config import DB_CONFIG

class Database:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or not cls._connection.open:
            cls._connection = pymysql.connect(**DB_CONFIG)
        return cls._connection

    @classmethod
    def execute_query(cls, query, params=None, fetch=False):
        conn = cls.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id