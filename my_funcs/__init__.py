import datetime
import sqlite3
from dataclasses import dataclass

from sqlalchemy import create_engine

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from app import Sequence

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sequences.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@dataclass
class Sequence:
    name: str
    url: str


def insSequence(store, url, name):
#    conn = sqlite3.connect("c:\Users\elcrapamundo\PycharmProjects\app\sequences.db")
#    c = conn.cursor()
 #   current_date = datetime.datetime.now()

  #  c.execute(
   #     """DELETE from sequences where url=? AND storename = ?""",
    #    (
     #       url,
      #      store,
#        ),
 #   )
  #  c.execute(
   #     """INSERT into sequences VALUES(?,?,?,?)""", (store, url, name, current_date)
    sequence = Sequence(name, url)
    db.session.add(sequence)
    print(sequence)
    db.session.commit()

    c.close()


def create_database():
    engine = create_engine("postgresql://usr:pass@localhost:5432/sqlalchemy")
