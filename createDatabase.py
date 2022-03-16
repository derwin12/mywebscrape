import sqlite3

conn = sqlite3.connect('sequence.db')
c = conn.cursor()

c.execute('''CREATE TABLE sequences(storename, url, name, last_seen) ''')

c.close()