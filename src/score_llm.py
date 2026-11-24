"""Step 7 (optional): LLM scoring of hedging / evasiveness / confidence in the Q&A.

Contamination guard: an LLM may have *seen* how a famous call played out. We strip
years before sending, and you should disclose this limitation. Set ANTHROPIC_API_KEY
in your environment (never commit it).
"""
import json, re
import anthropic
from db import connect, save_scores
from segment import split_sections

MODEL = "claude-sonnet-5-5"
MAX_CHARS = 30000

PROMPT = """You are a financial analyst. Read this excerpt from an earnings call Q&A.
Return ONLY a JSON object with integer scores 0-10:
  "hedging": how much management qualifies/hedges answers (10 = extremely hedged),
  "evasiveness": how often questions are deflected or not directly answered,
  "confidence": confidence about forward-looking business outlook,
and "guidance": -1 (lowered/worse), 0 (unchanged/unclear), 1 (raised/better).
No other text.

EXCERPT:
{text}"""

def clean(text):
    return re.sub(r"\b(19|20)\d{2}\b", "[YEAR]", text)[:MAX_CHARS]

def run(limit=None):
    client = anthropic.Anthropic()
    con = connect()
    done = {r[0] for r in con.execute("SELECT transcript_id FROM scores WHERE method='llm'")}
    q = "SELECT id, text FROM transcripts" + (f" LIMIT {int(limit)}" if limit else "")
    for tid, text in con.execute(q).fetchall():
        if tid in done:
            continue
        _, qa, found = split_sections(text)
        if not found:
            continue
        msg = client.messages.create(model=MODEL, max_tokens=200, temperature=0,
                                     messages=[{"role": "user", "content": PROMPT.format(text=clean(qa))}])
        try:
            data = json.loads(re.search(r"\{.*\}", msg.content[0].text, re.S).group(0))
            save_scores(con, [(tid, "llm", "qa", k, float(data[k]))
                              for k in ("hedging", "evasiveness", "confidence", "guidance")])
        except Exception as e:
            print("parse failure", tid, e)

if __name__ == "__main__":
    run()
