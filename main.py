# main.py — QTest CLI

import hashlib, re
from claude_service import ask_claude, get_cost_summary

_cache:   dict = {}
_history: list = []
_stats:   dict = {"cache": 0, "claude": 0}

_STOPWORDS = {"what","is","the","are","do","does","you","have","any","a","an",
              "i","me","your","about","can","tell","know","please","there","for"}

def _cache_key(message: str) -> str:
    t = re.sub(r'[^\w\s]', '', message.lower())
    words = [w for w in t.split() if w not in _STOPWORDS]
    return hashlib.md5(" ".join(sorted(words)).encode()).hexdigest()

def _show_stats():
    total = sum(_stats.values()) or 1
    print(f"\n📊 Total={total} | Cache={_stats['cache']} | Claude={_stats['claude']}")
    print(f"💰 {get_cost_summary()}\n")

print("\n🤖 QTest Assistant  (type 'exit' or 'stats')\n")

while True:
    user = input("Student: ").strip()
    if not user:    continue
    if user.lower() == "exit":  _show_stats(); break
    if user.lower() == "stats": _show_stats(); continue

    k = _cache_key(user)

    if k in _cache:
        reply  = _cache[k]
        source = "cache 💾"
        _stats["cache"] += 1
    else:
        reply  = ask_claude(user, _history)
        _cache[k] = reply
        if len(_cache) > 500: del _cache[next(iter(_cache))]
        source = "claude 🤖"
        _stats["claude"] += 1

    print(f"\nAssistant [{source}]: {reply}\n" + "-"*50)

    _history.append({"role": "user",      "content": user})
    _history.append({"role": "assistant",  "content": reply})
    _history = _history[-4:]