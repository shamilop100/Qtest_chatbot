# claude_service.py — Claude fallback only
# Handles: unknown courses, general questions, joining interest

import time, logging, re
import anthropic
from config import CLAUDE_KEY, MODEL_NAME

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=CLAUDE_KEY)

with open("assistant_prompt.txt", encoding="utf-8") as f:
    _SYS = f.read()

_FALLBACK = "Sorry, I had a technical issue. Please call 9961 544 424."

_cost_usd = 0.0
_calls    = 0

def get_cost_summary():
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
    cost = (inp * 0.0000008) + (out * 0.000004)
    _cost_usd += cost
    _calls    += 1
    log.info(f"💰 in={inp} out={out} ₹{cost*83:.4f} | total ₹{_cost_usd*83:.4f}")

def ask_claude(message: str, intent: str, history: list = []) -> tuple[str, str]:
    trimmed = [{"role": m["role"], "content": m["content"][:100]} for m in history[-4:]]
    msgs = [*trimmed, {"role": "user", "content": message}]

    for attempt in range(3):
        try:
            r = client.messages.create(
                model       = MODEL_NAME,
                max_tokens  = 120,
                temperature = 0.3,
                system      = _SYS,
                messages    = msgs,
            )
            _track(r.usage)
            txt = next((b.text for b in r.content if b.type == "text"), None)
            return intent, (txt.strip() if txt else _FALLBACK)
        except anthropic.RateLimitError:
            log.warning(f"rate limit — retry {attempt+1}"); time.sleep(1.5)
        except Exception as e:
            log.error(f"Claude error: {e}"); break

    return intent, _FALLBACK