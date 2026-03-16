# 🤖 QTest Chatbot

> AI-powered student assistant for **QTest Software Solution LLP**, Kozhikode, Kerala — built on Claude 3 Haiku with a FastAPI backend and a CLI interface.

---

## ✨ What it does

QTest Chatbot answers prospective and current student queries about courses, fees, duration, syllabus, placements, and more — instantly, accurately, and only from verified institute data. It never hallucinates facts.

- 🎓 Covers **Manual Testing**, **Java & Selenium Automation**, and the combined **Master course**
- 💬 Dual interface — REST API (for web/mobile frontends) and a terminal CLI
- ⚡ MD5-based response cache cuts repeat API calls to zero
- 💰 Per-call cost tracker in USD and INR
- 🔄 Session memory — remembers the last 2 turns of conversation
- 🛡️ Strict system prompt — stays on-topic, never invents data

---

## 🗂️ Project structure

```
qtest-chatbot/
├── app.py               # FastAPI server  (/chat, /health, /stats)
├── main.py              # CLI interface
├── claude_service.py    # Anthropic API wrapper + cost tracker
├── institute_data.py    # Single source of truth — all course data
├── assistant_prompt.txt # System prompt template with {context} slot
├── hf_local.py          # Keyword-based intent detection (en)
├── config.py            # API key + model config (reads .env)
├── requirements.txt
└── .env                 # Your CLAUDE_KEY goes here (never commit this)
```

---

## 🚀 Quick start

### 1. Clone and install

```bash
git clone https://github.com/your-username/qtest-chatbot.git
cd qtest-chatbot
pip install -r requirements.txt
```

### 2. Set up your API key

Create a `.env` file in the project root:

```env
CLAUDE_KEY=sk-ant-...
```

> Get your key from [console.anthropic.com](https://console.anthropic.com)

### 3. Run the API server

```bash
uvicorn app:app --reload
```

Server starts at `http://localhost:8000`

### 4. Or run the CLI

```bash
python main.py
```

---

## 📡 API reference

### `POST /chat`

Send a student message and get a reply.

**Request**
```json
{
  "message": "What is the fee for Java Selenium course?",
  "session_id": "student_001"
}
```

**Response**
```json
{
  "reply": "The Java & Selenium Automation course is priced at ₹18,000 for a 3-month duration. For enrollment, call 9961 544 424 😊",
  "source": "claude"
}
```

`source` will be `"cache"` for repeated questions — no API cost.

---

### `GET /health`

```json
{ "status": "ok" }
```

---

### `GET /stats`

```json
{
  "breakdown": { "cache": 12, "claude": 5 },
  "total": 17,
  "cache_%": "71%",
  "claude_%": "29%",
  "cost": {
    "calls": 5,
    "usd": 0.000312,
    "inr": 0.0259,
    "avg_inr": 0.0052
  }
}
```

---

## 🧠 How it works

```
Student message
      │
      ▼
 Empty check
      │
      ▼
 MD5 cache key  ──── Cache hit? ──── YES ──▶ Return instantly
  (stopwords          │
   stripped,          NO
   words sorted)      │
                      ▼
              ask_claude(msg, history)
              ├── Trim history to last 4 msgs
              ├── Inject _SYSTEM prompt (built once at startup)
              ├── Call Anthropic API (3 retries on rate limit)
              └── Track token cost (₹ + $)
                      │
                      ▼
              Save to cache + session
                      │
                      ▼
              Return reply + source tag
```

**System prompt** is built once at startup by injecting `institute_data.py` content into `assistant_prompt.txt` — so every Claude call carries the full institute context without re-reading files.

---

## 📚 Courses covered

| Course | Fee | Duration |
|---|---|---|
| Manual Testing | ₹10,000 | 3 months |
| Java & Selenium Automation | ₹18,000 | 3 months |
| Java Selenium + Manual Master | ₹28,000 | 3 months |

All courses include:
- ✅ 100% Placement Assistance
- ✅ Industry-recognised Certificate
- ✅ Free demo class available
- ✅ Online & Offline batches
- ✅ Night & Sunday batches for working professionals

📍 **Emerald Mall, Mavoor Road, Kozhikode, Kerala**
📞 **9961 544 424** | 🌐 [qtestsolutions.com](http://www.qtestsolutions.com)

---

## ⚙️ Configuration

| Variable | File | Description |
|---|---|---|
| `CLAUDE_KEY` | `.env` | Anthropic API key |
| `MODEL_NAME` | `config.py` | Model (`claude-3-haiku-20240307`) |
| `max_tokens` | `claude_service.py` | Max reply length (default: 150) |
| `temperature` | `claude_service.py` | Creativity (default: 0.3) |
| Cache size cap | `app.py` / `main.py` | Max cached entries (default: 500) |
| History window | `claude_service.py` | Msgs kept per session (default: 4) |

---

## 🔌 Intent detection (hf_local.py)

A lightweight, zero-dependency keyword classifier detects query intent before hitting Claude. No GPU, no model downloads — just fast string matching.

Detected intents: `greeting`, `pricing`, `duration`, `syllabus`, `placement`, `certificate`, `demo`, `online_offline`, `location`

> Currently available as a utility — ready to be wired in for pre-routing, analytics, or fallback handling.

---

## 💡 Extending the project

- **Add a new course** — edit `institute_data.py`. The system prompt updates automatically on next server start.
- **Change the bot's tone** — edit `assistant_prompt.txt`.
- **Connect a frontend** — point your React/Flutter app at `POST /chat` with a `session_id` per user.
- **Wire in intent detection** — call `get_hint(message)` in `app.py` before the cache check to log or route by intent.
- **Persist sessions** — replace the in-memory `_sessions` dict with Redis for multi-worker deployments.

---

## 📦 Requirements

```
anthropic
python-dotenv
fastapi
uvicorn
pydantic
```

Python 3.10+ recommended.

---

## 🔒 Security notes

- Never commit `.env` to version control — add it to `.gitignore`
- The API has no authentication by default — add an API key header or rate limiting before exposing to the internet
- CORS is set to `allow_origins=["*"]` for development — restrict this in production

---

## 📄 License

MIT — free to use and adapt.

---

<p align="center">Built with ❤️ for QTest Software Solution LLP, Kozhikode</p>
