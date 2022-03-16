import sqlite3

conn = sqlite3.connect('sequence.db')
c = conn.cursor()

c.execute('''DELETE from sequences where url = 'someurl' ''')
c.execute('''INSERT into sequences VALUES(?,?,?,datetime("now"))''', ('somestore','someurl', 'name'))
conn.commit()

c.execute('''SELECT * from sequences''')
results = c.fetchall()
print(results)

c.close()