import sqlite3

with sqlite3.connect('pyzza.db') as connection:
    print('[*] Connection established')
    connection.execute('''
        CREATE TABLE users(
            user_name TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    print('[*] Users table created')
