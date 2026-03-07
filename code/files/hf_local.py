# hf_local.py — papluca/xlm-roberta-base-language-detection

import re
from transformers import pipeline

_detector = None

def _get_detector():
    global _detector
    if _detector is None:
        print("[hf_local] Loading language detection model (first time only)...")
        _detector = pipeline(
            "text-classification",
            model="papluca/xlm-roberta-base-language-detection"
        )
        print("[hf_local] Model loaded ✓")
    return _detector

_REPLACEMENTS = {
    "fees": "ഫീസ്", "fee": "ഫീസ്", "price": "വില",
    "duration": "ദൈർഘ്യം", "online": "ഓൺലൈൻ",
    "offline": "ഓഫ്ലൈൻ", "ethra": "എത്ര"
}

_INTENT_MAP = [
    ("greeting",      ["hi","hello","hai","namaskaram","vanakkam","hey","namasthe"]),
    ("pricing",       ["ഫീസ്","വില","fee","fees","price","cost","amount","rs","rupee",
                       "paisa","how much","ethra aanu","enthanu","എത്ര രൂപ"]),
    ("duration",      ["ദൈർഘ്യം","കാലം","month","months","days","week","naal",
                       "maasam","how long","ethra naal","എത്ര നാൾ"]),
    ("syllabus",      ["syllabus","topics","content","curriculum","subject",
                       "modules","padikkan","എന്ത് പഠിക്കും"]),
    ("placement",     ["job","placement","work","hire","career","company","ജോലി","guarantee"]),
    ("certificate",   ["certificate","cert","certified","യോഗ്യത","qualification"]),
    ("demo",          ["demo","trial","free class","free session","try"]),
    ("online_offline",["ഓൺലൈൻ","ഓഫ്ലൈൻ","zoom","online","offline","batch","from home"]),
    ("location",      ["എവിടെ","സ്ഥലം","address","near","location","centre","where","branch"]),
]

def _normalize(text: str) -> str:
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    return text

def get_hint(text: str) -> tuple[str, str]:
    lang = _get_detector()(text)[0]["label"]
    t = _normalize(text)
    for intent, keywords in _INTENT_MAP:
        if any(w in t for w in keywords):
            return lang, intent
    return lang, "other"
