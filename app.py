# app.py — QTest Chatbot API
#
# User → Cache check → Claude Haiku (with institute context) → Reply

import hashlib, re, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from claude_service import ask_claude, get_cost_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="QTest Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

_cache:    dict = {}
_sessions: dict = {}
_stats:    dict = {"cache": 0, "claude": 0}

_STOPWORDS = {"what","is","the","are","do","does","you","have","any","a","an",
              "i","me","your","about","can","tell","know","please","there","for"}

def _cache_key(message: str) -> str:
    t = re.sub(r'[^\w\s]', '', message.lower())
    words = [w for w in t.split() if w not in _STOPWORDS]
    return hashlib.md5(" ".join(sorted(words)).encode()).hexdigest()

class ChatRequest(BaseModel):
    message:    str
    session_id: str = "default"

@app.post("/chat")
async def chat(req: ChatRequest):
    user    = req.message.strip()
    session = req.session_id
    history = _sessions.get(session, [])

    if not user:
        return {"reply": "Please send a message 😊", "source": "system"}

    # ── Cache check ────────────────────────────────────────────────
    k = _cache_key(user)
    if k in _cache:
        log.info(f"💾 Cache hit: {user[:40]}")
        _stats["cache"] += 1
        return {"reply": _cache[k], "source": "cache"}

    # ── Claude Haiku ───────────────────────────────────────────────
    reply = ask_claude(user, history)

    # Save to cache
    _cache[k] = reply
    if len(_cache) > 500:
        del _cache[next(iter(_cache))]
    _stats["claude"] += 1

    # Save history
    history.append({"role": "user",      "content": user})
    history.append({"role": "assistant",  "content": reply})
    _sessions[session] = history[-4:]

    return {"reply": reply, "source": "claude"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    total = sum(_stats.values()) or 1
    return {
        "breakdown":  _stats,
        "total":      total,
        "cache_%":    f"{round(_stats['cache']/total*100)}%",
        "claude_%":   f"{round(_stats['claude']/total*100)}%",
        "cost":       get_cost_summary(),
    }