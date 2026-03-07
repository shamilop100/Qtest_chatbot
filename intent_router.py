# intent_router.py — detects intent and routes to correct layer

import re

# ── Intent keyword map ────────────────────────────────────────────
_INTENT_MAP = [
    ("greeting",      ["hi","hello","hey","good morning","good evening","good afternoon","namasthe"]),
    ("pricing",       ["fee","fees","price","cost","amount","rupee","how much","charge",
                       "pay","payment","budget","money","rate","tuition","pricing","rs"]),
    ("duration",      ["duration","month","months","days","week","how long","period",
                       "finish","complete","timeline","length","how many months"]),
    ("syllabus",      ["syllabus","topics","content","curriculum","subject","modules",
                       "learn","cover","teach","study","what is taught","what will i learn"]),
    ("placement",     ["placement","job","hire","career","guarantee","employ","recruit",
                       "opportunity","get placed","after course","assured","assist"]),
    ("certificate",   ["certificate","cert","certified","qualification","credential","proof"]),
    ("demo",          ["demo","trial","free class","free session","sample",
                       "preview","before joining","test class","demo class"]),
    ("online_offline",["online","offline","batch","from home","zoom","timing","schedule",
                       "weekend","night","sunday","flexible","class mode","virtual"]),
    ("location",      ["location","address","where","place","centre","center",
                       "branch","reach","directions","near","situated","find you"]),
    ("courses",       ["course","courses","program","programs","offer","available",
                       "options","which course","what course","what do you offer","all courses"]),
]

def _normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', ' ', text.lower())

def detect_intent(message: str) -> str:
    t = _normalize(message)
    for intent, keywords in _INTENT_MAP:
        if any(w in t for w in keywords):
            return intent
    return "other"

def detect_course(message: str) -> str | None:
    t = message.lower()
    if any(k in t for k in ["selenium","java","automation"]): return "selenium"
    if any(k in t for k in ["manual"]):                       return "manual"
    if any(k in t for k in ["combined","master","both"]):     return "combined"
    return None
