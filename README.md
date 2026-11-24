# Earnings Call Signal Lab

Do the *words* executives use on earnings calls predict how their stock performs afterward?
This repo ingests transcripts + prices, scores language (Loughran-McDonald dictionary, FinBERT,
an LLM), runs an event study with abnormal returns, and tests signals out-of-sample with a
multiple-testing correction.

## Quick start (verify everything works on synthetic data first)
```bash
pip install pandas numpy scipy openpyxl
SIGNAL_LAB_DEMO=1 python run_pipeline.py demo lm events analysis excel
python tests/test_events.py
```
Windows PowerShell: `$env:SIGNAL_LAB_DEMO=1; python run_pipeline.py demo lm events analysis excel`

## Real run
```bash
pip install -r requirements.txt
python run_pipeline.py prices transcripts lm events analysis excel
```
Needs: `data/transcripts.csv` and `data/Loughran-McDonald_MasterDictionary.csv` (see docs).

## Method (the parts that matter)
- **No look-ahead:** entry is the close of the first trading day *after* the call date.
- **Abnormal returns:** stock return minus beta x SPY, beta estimated only on pre-call data.
- **Controls:** the immediate price reaction is included so we test *drift*, not the reaction.
- **Inference:** ticker-clustered standard errors; Benjamini-Hochberg FDR across all tests.
- **Validation:** earliest 60% of events = train, latest 40% = test.

## Results
_Fill in after your real run: top findings, what failed, effect sizes, limitations._

## Limitations
_Survivorship bias (current index members), transcript timing ambiguity, small sample, LLM
training-data contamination, no transaction costs, sector-specific results._
