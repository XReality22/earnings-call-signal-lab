# Pre-registered hypotheses  (WRITE THIS BEFORE RUNNING ON REAL DATA, then commit it to git)

Date written: ____    Git commit hash: ____

| # | Hypothesis | Feature | Expected sign | Horizon |
|---|-----------|---------|---------------|---------|
| H1 | An increase in Q&A uncertainty language vs. last quarter predicts underperformance | lm_unc_qa_d | negative | 5-30d |
| H2 | Change in tone matters more than level of tone | lm_tone_full_d vs lm_tone_full | d stronger | 10d |
| H3 | Q&A carries more signal than scripted prepared remarks | lm_tone_qa_d vs lm_tone_prep_d | qa stronger | 10d |
| H4 | LLM-rated evasiveness predicts underperformance | llm_evasiveness_qa_d | negative | 30d |

Rules: (1) I will not add hypotheses after seeing results without labelling them "exploratory".
(2) All results are reported, including the ones that failed.
(3) The test period (latest 40% of events) is looked at only once, at the end.
