# app.py — QTest Chatbot
#
# User
#  │
# Intent Router (intent_router.py)
#  │
#  ├── Knowledge Engine (institute_data.py) → instant, ₹0
#  │
#  ├── Cache                                → instant, ₹0
#  │
#  └── Claude                               → fallback only, billed

import hashlib, re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from intent_router import detect_intent, detect_course
from institute_data import get_answer
from claude_service import ask_claude, get_cost_summary

app = FastAPI(title="QTest Chatbot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_cache:    dict = {}
_sessions: dict = {}
_stats:    dict = {"knowledge": 0, "cache": 0, "claude": 0}

_STOPWORDS = {"what","is","the","are","do","does","you","have","any","a","an",
              "i","me","your","about","can","tell","know","please","there","for"}

def _cache_key(message: str, intent: str) -> str:
    t = re.sub(r'[^\w\s]', '', message.lower())
    words = [w for w in t.split() if w not in _STOPWORDS]
    norm = " ".join(sorted(words))
    return hashlib.md5(f"{norm}|{intent}".encode()).hexdigest()

class ChatRequest(BaseModel):
    message:    str
    session_id: str = "default"

@app.post("/chat")
async def chat(req: ChatRequest):
    user    = req.message.strip()
    session = req.session_id
    history = _sessions.get(session, [])

    if not user:
        return {"reply": "Please send a message 😊"}

    # ── Step 1: Intent Router ──────────────────────────────────────
    intent = detect_intent(user)
    course = detect_course(user)

    # ── Step 2: Knowledge Engine ───────────────────────────────────
    reply = get_answer(intent, course)
    if reply:
        source = "knowledge"
        _stats["knowledge"] += 1

    else:
        # ── Step 3: Cache ──────────────────────────────────────────
        k = _cache_key(user, intent)
        if k in _cache:
            reply  = _cache[k]
            source = "cache"
            _stats["cache"] += 1

        # ── Step 4: Claude (fallback only) ─────────────────────────
        else:
            _, reply = ask_claude(user, intent, history)
            _cache[k] = reply
            if len(_cache) > 200: del _cache[next(iter(_cache))]
            source = "claude"
            _stats["claude"] += 1

    # ── Save history ───────────────────────────────────────────────
    history.append({"role": "user",      "content": user})
    history.append({"role": "assistant",  "content": reply})
    _sessions[session] = history[-4:]

    return {"intent": intent, "reply": reply, "source": source}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    total  = sum(_stats.values()) or 1
    claude = _stats["claude"]
    return {
        "breakdown": _stats,
        "total":     total,
        "claude_%":  f"{round(claude/total*100)}%",
        "saved_%":   f"{round((_stats['knowledge']+_stats['cache'])/total*100)}%",
        "cost":      get_cost_summary(),
    }