"""Synthetic data with a PLANTED weak signal, so you can verify the pipeline end to end
(and confirm it can detect a real effect) before touching real data. Demo mode only."""
import os
import numpy as np
import pandas as pd
from config import DEMO, DATA_DIR, LM_PATH, TICKERS, BENCHMARK, HORIZONS
from db import connect

NEG = ["decline", "weak", "loss", "impairment", "adverse", "difficult", "challenging", "downturn"]
POS = ["strong", "growth", "improved", "record", "exceeded", "confident", "gain", "success"]
UNC = ["uncertain", "may", "could", "approximately", "risk", "unclear", "volatility", "depend"]
NEU = ["revenue", "quarter", "customers", "platform", "margin", "we", "our", "the", "and", "of",
       "cloud", "demand", "product", "pipeline", "growth", "mix", "cost", "spend"]
PLANT = 0.0006     # daily drift per 1 unit of tone change, applied after entry

def make_text(rng, tone, n=700):
    p_pos, p_neg = 0.04 + 0.012 * tone, 0.04 - 0.012 * tone
    p_unc = 0.04
    probs = np.array([max(p_pos, 0.005), max(p_neg, 0.005), p_unc])
    neu = 1 - probs.sum()
    words = rng.choice(["P", "N", "U", "X"], size=n, p=np.append(probs, neu))
    out = []
    for w in words:
        out.append(rng.choice(POS) if w == "P" else rng.choice(NEG) if w == "N"
                   else rng.choice(UNC) if w == "U" else rng.choice(NEU))
    return " ".join(out)

def run(seed=7):
    assert DEMO, "Run demo mode with SIGNAL_LAB_DEMO=1"
    rng = np.random.default_rng(seed)
    pd.DataFrame({"Word": [w.upper() for w in NEG + POS + UNC],
                  "Negative": [1] * len(NEG) + [0] * (len(POS) + len(UNC)),
                  "Positive": [0] * len(NEG) + [1] * len(POS) + [0] * len(UNC),
                  "Uncertainty": [0] * (len(NEG) + len(POS)) + [1] * len(UNC)}).to_csv(LM_PATH, index=False)

    dates = pd.bdate_range("2018-01-01", "2025-12-31")
    mkt = rng.normal(0.0004, 0.01, len(dates))
    tickers = TICKERS[:20]
    rets, events = {}, []
    for tk in tickers:
        beta = rng.uniform(0.8, 1.5)
        r = beta * mkt + rng.normal(0, 0.015, len(dates))
        tone_prev, d0 = rng.normal(), pd.Timestamp("2019-02-01") + pd.Timedelta(days=int(rng.integers(0, 40)))
        for q in range(28):
            call = d0 + pd.Timedelta(days=91 * q + int(rng.integers(-4, 5)))
            call = call + pd.offsets.BDay(0)
            tone = rng.normal()
            delta = tone - tone_prev
            tone_prev = tone
            t0 = dates.searchsorted(call)
            entry = t0 + 1
            if entry + max(HORIZONS) + 1 < len(dates):
                r[entry + 1: entry + 1 + 30] += PLANT * delta       # planted post-call drift
            events.append((tk, call.strftime("%Y-%m-%d"), call.year, (q % 4) + 1, tone))
        rets[tk] = r
    px = pd.DataFrame({tk: 100 * np.cumprod(1 + r) for tk, r in rets.items()}, index=dates)
    px[BENCHMARK] = 100 * np.cumprod(1 + mkt)

    con = connect()
    con.execute("DELETE FROM prices"); con.execute("DELETE FROM transcripts"); con.execute("DELETE FROM scores")
    long = px.reset_index(names="date").melt(id_vars="date", var_name="ticker", value_name="adj_close")
    long["date"] = long["date"].dt.strftime("%Y-%m-%d")
    long[["ticker", "date", "adj_close"]].to_sql("prices", con, if_exists="append", index=False)
    rows = []
    seen = set()
    for tk, d, fy, qn, tone in events:
        if (tk, fy, qn) in seen:
            continue
        seen.add((tk, fy, qn))
        prep = make_text(rng, tone)
        qa = "Question-and-Answer Session " + make_text(rng, tone + rng.normal(0, 0.5))
        rows.append((tk, d, fy, qn, prep + " " + qa))
    con.executemany("INSERT INTO transcripts (ticker, call_date, fiscal_year, quarter, text) VALUES (?,?,?,?,?)", rows)
    con.commit()
    print(f"Demo: {len(rows)} synthetic transcripts, {len(tickers)} tickers (planted signal strength {PLANT})")

if __name__ == "__main__":
    run()
