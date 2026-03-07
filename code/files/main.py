# main.py — QTest Student Assistant (3-layer Claude hit reduction)

import hashlib
from hf_local import get_hint
from claude_service import ask_claude

_STATIC = {
    "greeting": "Hello! Welcome to QTest Software Solutions 😊 How can I help you?",
    "location": "📍 Emerald Mall, Mavoor Road, Kozhikode\n📞 9961 544 424\n🌐 www.qtestsolutions.com",
}
_cache, history, stats = {}, [], {"static":0,"cache":0,"claude":0}

def _key(m, h): return hashlib.md5(f"{m.lower().strip()}|{h}".encode()).hexdigest()

def _show_stats():
    t = sum(stats.values()) or 1
    s = stats["static"] + stats["cache"]
    print(f"\n📊 Stats: Total={t} | Static={stats['static']} | Cache={stats['cache']} | Claude={stats['claude']} | 💰 Saved={round(s/t*100)}%\n")

print("\n🤖 QTest Assistant  (exit/clear)\n")

while True:
    user = input("Student: ").strip()
    if not user: continue
    if user.lower() == "exit":  _show_stats(); break
    if user.lower() == "clear": _cache.clear(); history.clear(); stats.update(static=0,cache=0,claude=0); print("[Cleared]\n"); continue

    lang, hint = get_hint(user)

    # Layer 1 — static
    if hint in _STATIC:
        reply, intent = _STATIC[hint], hint
        stats["static"] += 1
        print(f"\nAssistant: {reply}  [⚡]\n" + "-"*50)

    # Layer 2 — cache
    elif _key(user, hint) in _cache:
        intent, reply = _cache[_key(user, hint)]
        stats["cache"] += 1
        print(f"\nAssistant: {reply}  [💾]\n" + "-"*50)

    # Layer 3 — Claude
    else:
        intent, reply = ask_claude(user, hint, history)
        _cache[_key(user, hint)] = (intent, reply)
        if len(_cache) > 200: del _cache[next(iter(_cache))]
        stats["claude"] += 1
        print(f"\nAssistant: {reply}  [🤖]\n" + "-"*50)

    history.append({"role":"user",      "content": f"MSG: {user}\nHINT: {hint}"})
    history.append({"role":"assistant", "content": f"INTENT: {intent}\nREPLY: {reply}"})
