import sqlite3
import os.path

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pyzza.db')

def create_user(user_name, password):
    with sqlite3.connect(DATABASE_PATH) as connection:
        print('[*] Connection established')
        connection.execute('''
            INSERT INTO users (user_name, password)
            VALUES (?, ?);
        ''', (user_name, password))
    print('[*] User created')


def get_user(user_name):
    with sqlite3.connect(DATABASE_PATH) as connection:
        print('[*] Connection established')
        cursor = connection.execute('''
            SELECT * FROM users
            WHERE user_name = ?;
        ''', (user_name,))
    return cursor.fetchone()
