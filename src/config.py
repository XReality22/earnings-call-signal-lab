"""Central settings. Edit this file, not the other modules."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = os.environ.get("SIGNAL_LAB_DEMO") == "1"          # demo mode uses synthetic data
DATA_DIR = ROOT / "data" / ("demo" if DEMO else "")
OUT_DIR = ROOT / "outputs" / ("demo" if DEMO else "")
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "signal_lab.db"
LM_PATH = DATA_DIR / "Loughran-McDonald_MasterDictionary.csv"
TRANSCRIPT_CSV = DATA_DIR / "transcripts.csv"

# ---- Universe: pick ONE sector and stay focused. Edit freely. ----
# Example: large-cap tech/software. Note: using today's index members creates
# survivorship bias. Say so in your limitations section.
TICKERS = [
    "AAPL", "MSFT", "NVDA", "ORCL", "ADBE", "CRM", "CSCO", "INTC", "AMD", "QCOM",
    "TXN", "AVGO", "IBM", "INTU", "AMAT", "MU", "ADI", "LRCX", "KLAC", "NOW",
    "SNPS", "CDNS", "PANW", "FTNT", "ADSK", "HPQ", "NTAP", "STX", "WDC", "GLW",
]
BENCHMARK = "SPY"
PRICE_START = "2018-01-01"

# ---- Event-study design (these choices matter: defend them in interviews) ----
ENTRY_LAG = 1          # enter at close of the 1st trading day AFTER the call date.
                       # We don't know if the call was pre-open or post-close, so this
                       # guarantees the signal was public before our entry. No look-ahead.
HORIZONS = [5, 10, 30]  # trading days held after entry
BETA_WINDOW = (250, 30) # estimate beta on days [t-250, t-30] before the call
MIN_BETA_OBS = 100
TRAIN_FRAC = 0.6        # earliest 60% of events = train, latest 40% = untouched test
