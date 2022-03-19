import sqlite3

conn = sqlite3.connect('sequence.db')
c = conn.cursor()

c.execute('''DROP TABLE IF EXISTS sequences''')
c.execute('''CREATE TABLE sequences(storename TEXT, url TEXT, name TEXT, last_seen DATE)''')

c.close()