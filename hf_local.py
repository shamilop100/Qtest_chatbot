# hf_local.py — Simple English keyword-based intent detection
# No HF model needed — fast, lightweight, no GPU required

import re

_INTENT_MAP = [
    ("greeting",       ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy"]),
    ("pricing",        ["fee", "fees", "price", "cost", "amount", "how much", "rupee", "rs", "inr", "charge", "pay"]),
    ("duration",       ["duration", "how long", "months", "weeks", "days", "long", "time", "period"]),
    ("syllabus",       ["syllabus", "topics", "content", "curriculum", "subjects", "modules", "what will", "what do", "learn", "cover", "covered"]),
    ("placement",      ["job", "placement", "hire", "career", "company", "guarantee", "work", "employ", "recruit"]),
    ("certificate",    ["certificate", "cert", "certified", "certification", "qualify", "qualification"]),
    ("demo",           ["demo", "trial", "free class", "free session", "try", "sample", "preview"]),
    ("online_offline", ["online", "offline", "zoom", "batch", "from home", "mode", "class type", "virtual"]),
    ("location",       ["address", "location", "where", "near", "branch", "centre", "center", "place", "map"]),
]

def _normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', ' ', text.lower())

def get_hint(text: str) -> tuple[str, str]:
    t = _normalize(text)
    for intent, keywords in _INTENT_MAP:
        if any(w in t for w in keywords):
            return "en", intent
    return "en", "other"