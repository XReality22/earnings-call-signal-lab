"""Step 3a: download adjusted daily closes into SQLite."""
import pandas as pd
import yfinance as yf
from config import TICKERS, BENCHMARK, PRICE_START
from db import connect

def run():
    con = connect()
    tickers = TICKERS + [BENCHMARK]
    df = yf.download(tickers, start=PRICE_START, auto_adjust=True, progress=False)["Close"]
    df.index.name = "Date"
    long = df.reset_index().melt(id_vars="Date", var_name="ticker", value_name="adj_close").dropna()
    long["date"] = pd.to_datetime(long["Date"]).dt.strftime("%Y-%m-%d")
    con.execute("DELETE FROM prices")
    long[["ticker", "date", "adj_close"]].to_sql("prices", con, if_exists="append", index=False)
    con.commit()
    n = con.execute("SELECT COUNT(DISTINCT ticker) FROM prices").fetchone()[0]
    print(f"Saved prices for {n} tickers (expected {len(tickers)})")

if __name__ == "__main__":
    run()
