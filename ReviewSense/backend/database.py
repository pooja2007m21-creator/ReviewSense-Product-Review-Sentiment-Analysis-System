import os, sqlite3
from contextlib import contextmanager

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database.db")

@contextmanager
def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()

def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS analyses(
            id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, label TEXT NOT NULL,
            confidence REAL, score REAL, word_count INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
