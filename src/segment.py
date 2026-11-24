"""Split a transcript into prepared remarks vs Q&A.

Heuristic: find the Q&A header, searching only after the first 15% of the text
(the operator's intro often *mentions* a Q&A session before it happens).
Spot-check 20 transcripts by hand and report the failure rate in your write-up.
"""
import re

QA_PATTERN = re.compile(
    r"(question[- ]and[- ]answer(?: session)?|questions? and answers?|q&a session|operator instructions)",
    re.I)

def split_sections(text: str):
    m = QA_PATTERN.search(text, pos=int(len(text) * 0.15))
    if not m:
        return text, "", False
    return text[:m.start()], text[m.start():], True
