"""Run with:  python -m pytest tests   (or: python tests/test_events.py)
These tests protect the two things interviewers probe hardest: look-ahead bias and beta leakage."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import numpy as np, pandas as pd
from config import BENCHMARK, ENTRY_LAG
import events

def synthetic(n=600, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    m = rng.normal(0, 0.01, n)
    px = pd.DataFrame({"AAA": 100 * np.cumprod(1 + 1.2 * m + rng.normal(0, 0.01, n)),
                       BENCHMARK: 100 * np.cumprod(1 + m)}, index=idx)
    return px, px.pct_change()

def test_entry_is_after_call_date():
    px, rets = synthetic()
    call = px.index[400]
    e = events.compute_event(px, rets, "AAA", call)
    assert pd.Timestamp(e["entry_date"]) > call            # no look-ahead

def test_pre_call_shock_does_not_change_post_call_ar():
    """Altering prices AFTER the beta window must not change beta (window ends 30d before call)."""
    px, rets = synthetic()
    call = px.index[400]
    base = events.compute_event(px, rets, "AAA", call)["beta"]
    px2 = px.copy(); px2.iloc[380:, 0] *= 1.5               # shock inside the 30 days before call
    rets2 = px2.pct_change()
    assert abs(events.compute_event(px2, rets2, "AAA", call)["beta"] - base) < 1e-9

def test_returns_unavailable_near_end_of_data_are_dropped():
    px, rets = synthetic()
    assert events.compute_event(px, rets, "AAA", px.index[-5]) is None

if __name__ == "__main__":
    for f in (test_entry_is_after_call_date, test_pre_call_shock_does_not_change_post_call_ar,
              test_returns_unavailable_near_end_of_data_are_dropped):
        f(); print("PASS", f.__name__)
