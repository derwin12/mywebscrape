import sqlite3
import pprint

conn = sqlite3.connect('sequence.db')
c = conn.cursor()

c.execute('''SELECT storename, name from sequences ORDER BY storename, name''')
results = c.fetchall()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(results)

c.close()