# main.py — QTest CLI client (mirrors app.py architecture)

from intent_router import detect_intent, detect_course
from institute_data import get_answer
from claude_service import ask_claude, get_cost_summary
import hashlib, re

_cache   = {}
_history = []
_stats   = {"knowledge": 0, "cache": 0, "claude": 0}

_STOPWORDS = {"what","is","the","are","do","does","you","have","any","a","an",
              "i","me","your","about","can","tell","know","please","there","for"}

def _cache_key(msg, intent):
    t = re.sub(r'[^\w\s]', '', msg.lower())
    words = [w for w in t.split() if w not in _STOPWORDS]
    return hashlib.md5(f"{' '.join(sorted(words))}|{intent}".encode()).hexdigest()

def _stats_display():
    total = sum(_stats.values()) or 1
    saved = _stats["knowledge"] + _stats["cache"]
    print(f"\n📊 Total={total} | Knowledge={_stats['knowledge']} | "
          f"Cache={_stats['cache']} | Claude={_stats['claude']} | "
          f"Saved={round(saved/total*100)}%")
    print(f"💰 {get_cost_summary()}\n")

print("\n🤖 QTest Assistant  (type 'exit' or 'stats')\n")

while True:
    user = input("Student: ").strip()
    if not user: continue
    if user.lower() == "exit":  _stats_display(); break
    if user.lower() == "stats": _stats_display(); continue

    # Step 1: Intent Router
    intent = detect_intent(user)
    course = detect_course(user)

    # Step 2: Knowledge Engine
    reply = get_answer(intent, course)
    if reply:
        source = "knowledge ⚡"
        _stats["knowledge"] += 1
    else:
        # Step 3: Cache
        k = _cache_key(user, intent)
        if k in _cache:
            reply  = _cache[k]
            source = "cache 💾"
            _stats["cache"] += 1
        # Step 4: Claude fallback
        else:
            _, reply = ask_claude(user, intent, _history)
            _cache[k] = reply
            if len(_cache) > 200: del _cache[next(iter(_cache))]
            source = "claude 🤖"
            _stats["claude"] += 1

    print(f"\nAssistant [{source}]: {reply}\n" + "-"*50)
    _history.append({"role": "user",      "content": user})
    _history.append({"role": "assistant",  "content": reply})
    _history = _history[-4:]