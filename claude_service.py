# claude_service.py

import time, logging
import anthropic
from config import CLAUDE_KEY, MODEL_NAME
from institute_data import get_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=CLAUDE_KEY)

# Build system prompt once with institute context injected
with open("assistant_prompt.txt", encoding="utf-8") as f:
    _PROMPT_TEMPLATE = f.read()

_SYSTEM = _PROMPT_TEMPLATE.replace("{context}", get_context())

# ── Cost tracker ───────────────────────────────────────────────────
_cost_usd = 0.0
_calls    = 0

def get_cost_summary() -> dict:
    return {
        "calls":   _calls,
        "usd":     round(_cost_usd, 6),
        "inr":     round(_cost_usd * 83, 4),
        "avg_inr": round(_cost_usd * 83 / _calls, 4) if _calls else 0,
    }

def _track(usage):
    global _cost_usd, _calls
    inp  = getattr(usage, "input_tokens",  0)
    out  = getattr(usage, "output_tokens", 0)
    cost = (inp * 0.00000025) + (out * 0.00000125)  # Claude 3 Haiku pricing
    _cost_usd += cost
    _calls    += 1
    log.info(f"💰 in={inp} out={out} ₹{cost*83:.4f} | total ₹{_cost_usd*83:.4f}")

# ── Main ask function ──────────────────────────────────────────────
def ask_claude(message: str, history: list = []) -> str:
    # Build messages — last 4 messages (2 turns) for context
    trimmed = [
        {"role": m["role"], "content": m["content"][:150]}
        for m in history[-4:]
    ]
    msgs = [*trimmed, {"role": "user", "content": message}]

    for attempt in range(3):
        try:
            r = client.messages.create(
                model       = MODEL_NAME,
                max_tokens  = 150,
                temperature = 0.3,
                system      = _SYSTEM,
                messages    = msgs,
            )
            _track(r.usage)
            txt = next((b.text for b in r.content if b.type == "text"), None)
            return txt.strip() if txt else "Sorry, please call 9961 544 424."

        except anthropic.RateLimitError:
            log.warning(f"Rate limit — retry {attempt+1}")
            time.sleep(1.5)
        except Exception as e:
            log.error(f"Claude error: {e}")
            break

    return "Sorry, I had a technical issue. Please call 9961 544 424."