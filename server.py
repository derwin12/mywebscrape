from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    con = sqlite3.connect('sequence.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM sequences ORDER BY storename, name")
    rows = cur.fetchall()

    return render_template('sequences.html', title='Sequences list',
                           rows=rows)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
