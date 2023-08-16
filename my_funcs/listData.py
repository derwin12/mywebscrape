import sqlite3
import pprint

conn = sqlite3.connect('..\\app\\sequences.db')
c = conn.cursor()

c.execute('''SELECT id, name from sequence ORDER BY name''')
results = c.fetchall()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(results)

c.close()
