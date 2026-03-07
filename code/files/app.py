# app.py — QTest Chatbot Web Server

import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hf_local import get_hint
from claude_service import ask_claude, get_cost_summary

app = FastAPI(title="QTest Chatbot API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_STATIC = {
    "greeting": "നമസ്കാരം! QTest Software Solution-ലേക്ക് സ്വാഗതം 😊 എന്ത് സഹായം വേണം?",
    "location": "📍 Emerald Mall, Mavoor Road, Kozhikode\n📞 9961 544 424\n🌐 www.qtestsolutions.com",
}
_cache:    dict = {}
_sessions: dict = {}
_stats:    dict = {"static": 0, "cache": 0, "claude": 0}

class ChatRequest(BaseModel):
    message:    str
    session_id: str = "default"

@app.post("/chat")
async def chat(req: ChatRequest):
    user    = req.message.strip()
    session = req.session_id
    history = _sessions.get(session, [])
    if not user:
        return {"intent": "other", "reply": "ദയവായി ഒരു message അയക്കൂ."}

    lang, hint = get_hint(user)
    key = hashlib.md5(f"{user.lower()}|{hint}".encode()).hexdigest()

    if hint in _STATIC:
        intent, reply = hint, _STATIC[hint]
        _stats["static"] += 1
        source = "static"
    elif key in _cache:
        intent, reply = _cache[key]
        _stats["cache"] += 1
        source = "cache"
    else:
        intent, reply = ask_claude(user, hint, history)
        _cache[key] = (intent, reply)
        if len(_cache) > 200: del _cache[next(iter(_cache))]
        _stats["claude"] += 1
        source = "claude"

    history.append({"role": "user",      "content": f"MSG: {user}\nHINT: {hint}"})
    history.append({"role": "assistant",  "content": f"INTENT: {intent}\nREPLY: {reply}"})
    _sessions[session] = history[-6:]

    return {"intent": intent, "reply": reply, "source": source}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    total = sum(_stats.values()) or 1
    saved = _stats["static"] + _stats["cache"]
    return {
        "messages"       : _stats,
        "claude_saved"   : f"{round(saved/total*100)}%",
        "cost"           : get_cost_summary(),
    }
