"""Step 3b: load earnings call transcripts into SQLite.

Transcripts come from a CSV with columns:
    ticker, call_date (YYYY-MM-DD), fiscal_year, quarter (1-4), text
This keeps the source swappable (a Kaggle/Hugging Face dataset, an API pull, or a
purchased file) without touching anything downstream.
"""
import pandas as pd
from config import TRANSCRIPT_CSV, TICKERS
from db import connect

REQUIRED = {"ticker", "call_date", "fiscal_year", "quarter", "text"}

def run(path=TRANSCRIPT_CSV, restrict_to_universe=True):
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    df["call_date"] = pd.to_datetime(df["call_date"]).dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.len() > 2000]          # drop stubs / truncated pages
    if restrict_to_universe:
        df = df[df["ticker"].isin(TICKERS)]
    con = connect()
    con.executemany(
        "INSERT OR IGNORE INTO transcripts (ticker, call_date, fiscal_year, quarter, text) VALUES (?,?,?,?,?)",
        df[["ticker", "call_date", "fiscal_year", "quarter", "text"]].values.tolist())
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
    print(f"{n} transcripts in database")

if __name__ == "__main__":
    run()
