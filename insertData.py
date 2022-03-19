import sqlite3
import datetime

def insSequence(store, url, name):
    conn = sqlite3.connect('sequence.db')
    c = conn.cursor()
    current_date = datetime.datetime.now()

    c.execute('''DELETE from sequences where url=? AND storename = ?''', (url,store,))
    c.execute('''INSERT into sequences VALUES(?,?,?,?)''', (store,url, name, current_date))
    conn.commit()

    c.close()