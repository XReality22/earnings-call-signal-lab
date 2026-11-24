"""Step 5b: turn raw scores into model features.

For every score we create:
    <feat>      the level
    <feat>_d    change vs the same company's previous quarter
    *_z         cross-sectional z-score within the calendar quarter (removes time effects)
"""
import numpy as np
import pandas as pd
from db import connect

def build():
    con = connect()
    t = pd.read_sql("SELECT id AS transcript_id, ticker, call_date FROM transcripts", con, parse_dates=["call_date"])
    s = pd.read_sql("SELECT * FROM scores WHERE method != 'meta'", con)
    s["feat"] = s["method"] + "_" + s["metric"] + "_" + s["section"]
    keep = s[~s["metric"].isin(["words", "pos", "neg"])]          # keep a focused feature set
    w = keep.pivot_table(index="transcript_id", columns="feat", values="value")
    df = t.merge(w, on="transcript_id").sort_values(["ticker", "call_date"]).reset_index(drop=True)
    feats = list(w.columns)
    g = df.groupby("ticker")
    gap = g["call_date"].diff().dt.days
    for f in feats:
        d = df[f] - g[f].shift(1)
        d[(gap < 60) | (gap > 130)] = np.nan       # only compare consecutive quarters
        df[f + "_d"] = d
    df["period"] = df["call_date"].dt.to_period("Q").astype(str)
    for c in feats + [f + "_d" for f in feats]:
        grp = df.groupby("period")[c]
        df[c + "_z"] = (df[c] - grp.transform("mean")) / grp.transform("std")
    return df

if __name__ == "__main__":
    print(build().head())
