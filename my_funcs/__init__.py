import datetime
import sqlite3
from dataclasses import dataclass

from sqlalchemy import create_engine


@dataclass
class Sequence:
    name: str
    url: str


def insSequence(store, url, name):
    conn = sqlite3.connect("sequence.db")
    c = conn.cursor()
    current_date = datetime.datetime.now()

    c.execute(
        """DELETE from sequences where url=? AND storename = ?""",
        (
            url,
            store,
        ),
    )
    c.execute(
        """INSERT into sequences VALUES(?,?,?,?)""", (store, url, name, current_date)
    )
    conn.commit()

    c.close()


def create_database():
    engine = create_engine("postgresql://usr:pass@localhost:5432/sqlalchemy")
