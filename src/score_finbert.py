"""Step 6 (optional): FinBERT sentence-level sentiment. Slow on CPU: start with a sample."""
import re
import numpy as np
from transformers import pipeline
from db import connect, save_scores
from segment import split_sections

MAX_SENT = 300     # evenly sample this many sentences per section to bound runtime

def sentences(text):
    s = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if len(x.strip()) > 25]
    if len(s) > MAX_SENT:
        s = [s[i] for i in np.linspace(0, len(s) - 1, MAX_SENT).astype(int)]
    return s

def run(limit=None):
    clf = pipeline("text-classification", model="ProsusAI/finbert", top_k=None,
                   truncation=True, max_length=256)
    con = connect()
    q = "SELECT id, text FROM transcripts" + (f" LIMIT {int(limit)}" if limit else "")
    rows = []
    for tid, text in con.execute(q).fetchall():
        prep, qa, found = split_sections(text)
        for sec, txt in (("prep", prep), ("qa", qa)):
            if not txt:
                continue
            out = clf(sentences(txt), batch_size=16)
            tone = np.mean([next(d["score"] for d in o if d["label"] == "positive") -
                            next(d["score"] for d in o if d["label"] == "negative") for o in out])
            rows.append((tid, "finbert", sec, "tone", float(tone)))
        print("scored", tid)
    save_scores(con, rows)

if __name__ == "__main__":
    run()
