# Pre-registered hypotheses

Date written: 2026-11-23

Git commit hash: The SHA of the commit containing this document is recorded in git history.

## Scope and data

- Universe: the 30 software and semiconductor companies listed in `src/config.py`.
- Data: real earnings transcripts and daily prices covering events after 2018-01-01.
- Entry: the close of the first trading day after the call date.
- Baseline: market-adjusted abnormal return using pre-call beta estimated over trading days
  [call date minus 250, call date minus 30] relative to SPY.
- Primary horizons: 5, 10, and 30 trading days after entry.
- Validation: earliest 60% of events is training data; latest 40% is the untouched test period.
- Missing or invalid events are excluded only according to the documented pipeline rules.
- The test period will be evaluated once, after the full pre-registered analysis plan is run.

## Hypotheses

| # | Hypothesis | Feature | Expected sign | Horizon |
|---|------------|---------|---------------|---------|
| H1 | An increase in Q&A uncertainty language relative to the same company's prior quarter predicts lower subsequent abnormal returns. | `lm_unc_qa_d` | Negative | 5, 10, 30 trading days |
| H2 | Quarter-over-quarter change in overall tone predicts abnormal returns more consistently than the level of overall tone. | `lm_tone_full_d` vs. `lm_tone_full` | Change feature is stronger in the same-sign out-of-sample test | 10 trading days |
| H3 | Quarter-over-quarter change in Q&A tone predicts abnormal returns more strongly than quarter-over-quarter change in prepared-remarks tone. | `lm_tone_qa_d` vs. `lm_tone_prep_d` | Both negative or positive in the direction of tone; Q&A change has the larger absolute coefficient and OOS IC | 10 trading days |
| H4 | LLM-rated Q&A evasiveness predicts lower subsequent abnormal returns. | `llm_evasiveness_qa_d` | Negative | 30 trading days |

## Primary analysis and decision rules

- The primary test for each hypothesis is the ticker-clustered OLS coefficient, controlling
  for the immediate post-call abnormal return (`react_ar`).
- Secondary evidence includes Spearman rank correlation and top-minus-bottom tercile spread.
- Directional predictions in the table will be tested as specified; H2 and H3 are comparative
  hypotheses, so their stronger-signal interpretation will be preregistered only on the basis
  of effect size and same-sign out-of-sample IC.
- Benjamini-Hochberg correction will be applied across the reported feature-horizon tests.
- A finding is considered statistically robust for the FDR decision only if adjusted p-value
  `p_fdr < 0.10` and the train/test information coefficients have the same sign.
- Any feature or result not included in this table is exploratory unless formally added here
  before real-data results are inspected.

## Reporting rules

1. I will not add hypotheses after seeing real-data results without labeling them "exploratory".
2. I will report all prespecified results, including failed hypotheses.
3. I will not change feature definitions, horizons, model controls, train/test split, or
   universe after viewing real-data test-period results.
4. Exploratory findings may be discussed, but they will not be presented as preregistered tests.
