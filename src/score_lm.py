"""Step 4: Loughran-McDonald dictionary scoring (the academic standard for finance text).

Download the Master Dictionary CSV from the Notre Dame SRAF site (search
"Loughran McDonald master dictionary") and save it as data/Loughran-McDonald_MasterDictionary.csv
"""
import re
import pandas as pd
from config import LM_PATH
from db import connect, save_scores
from segment import split_sections

TOKEN = re.compile(r"[a-z']+")

def load_lm():
    df = pd.read_csv(LM_PATH)
    df.columns = [c.lower() for c in df.columns]
    df["word"] = df["word"].astype(str).str.lower()
    return {k: set(df.loc[df[k] > 0, "word"]) for k in ("negative", "positive", "uncertainty")}

def score_text(text, lm):
    toks = TOKEN.findall(text.lower())
    n = len(toks)
    if n < 100:
        return None
    neg = sum(t in lm["negative"] for t in toks)
    pos = sum(t in lm["positive"] for t in toks)
    unc = sum(t in lm["uncertainty"] for t in toks)
    return {"tone": (pos - neg) / n, "neg": neg / n, "pos": pos / n, "unc": unc / n, "words": n}

def run():
    lm = load_lm()
    con = connect()
    rows = []
    for tid, text in con.execute("SELECT id, text FROM transcripts").fetchall():
        prep, qa, found = split_sections(text)
        sections = {"full": text, "prep": prep}
        if found:
            sections["qa"] = qa
        for sec, txt in sections.items():
            s = score_text(txt, lm)
            if s:
                rows += [(tid, "lm", sec, k, v) for k, v in s.items()]
        rows.append((tid, "meta", "full", "qa_found", float(found)))
    save_scores(con, rows)
    n = con.execute("SELECT COUNT(DISTINCT transcript_id) FROM scores WHERE method='lm'").fetchone()[0]
    print(f"Scored {n} transcripts (LM)")

if __name__ == "__main__":
    run()
