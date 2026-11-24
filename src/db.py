import sqlite3
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    ticker TEXT, date TEXT, adj_close REAL, PRIMARY KEY (ticker, date));
CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT, call_date TEXT, fiscal_year INTEGER, quarter INTEGER, text TEXT,
    UNIQUE (ticker, fiscal_year, quarter));
CREATE TABLE IF NOT EXISTS scores (
    transcript_id INTEGER, method TEXT, section TEXT, metric TEXT, value REAL,
    PRIMARY KEY (transcript_id, method, section, metric));
"""

def connect():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    return con

def save_scores(con, rows):
    """rows: iterable of (transcript_id, method, section, metric, value)"""
    con.executemany("INSERT OR REPLACE INTO scores VALUES (?,?,?,?,?)", list(rows))
    con.commit()
