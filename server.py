from flask import Flask, render_template, request
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

@app.route('/search', methods=['GET', 'POST'])
def sequence():
    if request.method == 'POST':
        con = sqlite3.connect('sequence.db')
        cur = con.cursor()

        cur.execute("SELECT storename, name, url FROM sequences " +
                    "where lower(name) like lower(?) ORDER BY storename, name",
                    ("%{}%".format(request.form['search_string']),))
        return render_template("sequence.html", title='Found Sequences (' +
                                                      request.form['search_string'] + ')', records=cur.fetchall())

    return render_template('sequence.html', title='Find A Sequence')


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
