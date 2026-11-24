"""Step 5c: test whether language features predict post-call abnormal returns.

For every (feature, horizon) we report:
  * Spearman IC (rank correlation of feature vs abnormal return)
  * OLS of AR on feature + the immediate price reaction, with standard errors
    clustered by ticker (the same company's events are not independent)
  * Tercile spread: mean AR of top-third minus bottom-third within each quarter
  * IC on the TRAIN period and the untouched TEST period
  * Benjamini-Hochberg FDR-adjusted p-values, because testing many features
    guarantees some look "significant" by luck (multiple-testing / p-hacking)
"""
import numpy as np
import pandas as pd
from scipy import stats
from config import HORIZONS, TRAIN_FRAC, OUT_DIR
from db import connect
from features import build

def cluster_ols(y, x_cols, groups):
    """OLS with intercept and cluster-robust SEs. Returns coef, se, t, p for the FIRST regressor."""
    y = np.asarray(y, float)
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in x_cols])
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    codes, G = pd.factorize(groups)
    meat = np.zeros((k, k))
    for g in range(len(set(codes))):
        idx = codes == g
        s = X[idx].T @ u[idx]
        meat += np.outer(s, s)
    G = len(set(codes))
    corr = (G / (G - 1)) * ((n - 1) / (n - k))
    V = corr * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    t = b / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), df=G - 1))
    return b[1], se[1], t[1], p[1]

def bh_fdr(p):
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(p, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    prev = 1.0
    for rank, i in zip(range(n, 0, -1), order[::-1]):
        prev = min(prev, p[i] * n / rank)
        adj[i] = prev
    return adj

def ic(x, y):
    return stats.spearmanr(x, y)[0] if len(x) > 30 else np.nan

def run():
    con = connect()
    df = build().merge(pd.read_sql("SELECT * FROM events", con), on="transcript_id")
    zcols = [c for c in df.columns if c.endswith("_z")]
    cut = df["call_date"].quantile(TRAIN_FRAC)
    rows = []
    for z in zcols:
        for h in HORIZONS:
            y = f"ar_{h}"
            sub = df[[z, y, "react_ar", "ticker", "call_date", "period"]].dropna()
            if len(sub) < 60:
                continue
            rho, p_rho = stats.spearmanr(sub[z], sub[y])
            b, se, t, p = cluster_ols(sub[y], [sub[z], sub["react_ar"]], sub["ticker"])
            pct = sub.groupby("period")[z].rank(pct=True)
            top, bot = sub.loc[pct > 2 / 3, y], sub.loc[pct <= 1 / 3, y]
            spread = top.mean() - bot.mean()
            tr, te = sub[sub.call_date <= cut], sub[sub.call_date > cut]
            rows.append({"feature": z[:-2], "horizon_days": h, "n": len(sub),
                         "ic": rho, "coef": b, "t_stat": t, "p_value": p,
                         "tercile_spread": spread,
                         "ic_train": ic(tr[z], tr[y]), "ic_test": ic(te[z], te[y]),
                         "n_test": len(te)})
    res = pd.DataFrame(rows)
    if res.empty:
        raise RuntimeError("No results: check that transcripts, scores and events all exist.")
    res["p_fdr"] = bh_fdr(res["p_value"])
    res["survives_fdr"] = res["p_fdr"] < 0.10
    res["same_sign_oos"] = np.sign(res["ic_train"]) == np.sign(res["ic_test"])
    res = res.sort_values("p_value").reset_index(drop=True)
    res.to_csv(OUT_DIR / "results.csv", index=False)
    df.to_csv(OUT_DIR / "event_dataset.csv", index=False)
    print(res.head(10).round(4).to_string())
    return res

if __name__ == "__main__":
    run()
