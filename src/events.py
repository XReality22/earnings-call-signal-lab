"""Step 5a: event study. Compute abnormal returns after each earnings call.

Timeline (trading days, t0 = first trading day on/after call_date):
    entry  = close of t0 + ENTRY_LAG          <- earliest moment the signal is surely public
    exit   = entry + h trading days
    AR_h   = stock return - beta * SPY return over [entry, exit]
    react_ar = AR over [t0-1 close, entry close]  <- the immediate price reaction (control)
Beta is estimated ONLY on data before the call (window BETA_WINDOW) to avoid look-ahead.
"""
import pandas as pd
from config import BENCHMARK, HORIZONS, ENTRY_LAG, BETA_WINDOW, MIN_BETA_OBS
from db import connect

def compute_event(px, rets, ticker, call_date):
    """px/rets: DataFrames indexed by date (columns = tickers incl. benchmark). Returns dict or None."""
    if ticker not in px.columns:
        return None
    t0 = px.index.searchsorted(pd.Timestamp(call_date))
    entry = t0 + ENTRY_LAG
    if t0 < BETA_WINDOW[0] or entry + max(HORIZONS) >= len(px):
        return None
    lo, hi = t0 - BETA_WINDOW[0], t0 - BETA_WINDOW[1]
    r = rets.iloc[lo:hi][[ticker, BENCHMARK]].dropna()
    if len(r) < MIN_BETA_OBS:
        return None
    beta = r[ticker].cov(r[BENCHMARK]) / r[BENCHMARK].var()

    def ar(i, j):
        s = px[ticker].iloc[j] / px[ticker].iloc[i] - 1
        m = px[BENCHMARK].iloc[j] / px[BENCHMARK].iloc[i] - 1
        return s - beta * m

    out = {"beta": beta, "entry_date": px.index[entry].strftime("%Y-%m-%d"),
           "react_ar": ar(t0 - 1, entry)}
    for h in HORIZONS:
        out[f"ar_{h}"] = ar(entry, entry + h)
    return out

def run():
    con = connect()
    px = pd.read_sql("SELECT ticker, date, adj_close FROM prices", con, parse_dates=["date"]) \
           .pivot(index="date", columns="ticker", values="adj_close").sort_index()
    rets = px.pct_change()
    tr = pd.read_sql("SELECT id, ticker, call_date FROM transcripts", con)
    rows = []
    for _, r in tr.iterrows():
        e = compute_event(px, rets, r.ticker, r.call_date)
        if e:
            rows.append({"transcript_id": r.id, **e})
    ev = pd.DataFrame(rows)
    ev.to_sql("events", con, if_exists="replace", index=False)
    print(f"Computed {len(ev)} events out of {len(tr)} transcripts")

if __name__ == "__main__":
    run()
