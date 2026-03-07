import time, logging, json
import anthropic
from config import CLAUDE_KEY, MODEL_NAME
from institute_data import get_institute_info

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=CLAUDE_KEY)

with open("assistant_prompt.txt", encoding="utf-8") as f:
    _SYS = [{"type":"text","text":f.read(),"cache_control":{"type":"ephemeral"}}]

_INTENTS = {"pricing","duration","syllabus","demo","placement","certificate","online_offline","greeting","other"}
_FALLBACK = "INTENT: other\nREPLY: ക്ഷമിക്കണം, പ്രശ്നം ഉണ്ടായി. 9961 544 424 വിളിക്കൂ."

_TOOLS = [{
    "name": "get_institute_info",
    "description": "Get QTest institute data: fees, syllabus, duration, demo, placement, certificate, batches, location. ALWAYS call this. Never guess fees or details.",
    "input_schema": {
        "type": "object",
        "properties": {
            "intent": {"type":"string","enum":["pricing","duration","syllabus","demo","placement","certificate","online_offline","location","other"]},
            "course": {"type":"string","enum":["manual","selenium","combined"]}
        },
        "required": ["intent"]
    }
}]

# ── Cost tracker (manual — no litellm) ────────────────────────────
_cost_usd = 0.0
_calls    = 0

def get_cost_summary():
    return {"calls":_calls,"usd":round(_cost_usd,6),"inr":round(_cost_usd*83,4),
            "avg_inr":round(_cost_usd*83/_calls,4) if _calls else 0}

def _track(usage):
    global _cost_usd, _calls
    try:
        # Haiku pricing: $0.80/1M input, $4.00/1M output
        inp  = getattr(usage,"input_tokens",0)
        out  = getattr(usage,"output_tokens",0)
        cost = (inp * 0.0000008) + (out * 0.000004)
        _cost_usd += cost; _calls += 1
        log.info(f"💰 in={inp} out={out} ₹{cost*83:.4f} | total ₹{_cost_usd*83:.4f}")
    except Exception as e:
        log.warning(f"track err: {e}")

# ── Response parser ────────────────────────────────────────────────
def _parse(raw):
    intent, reply = "other", raw.strip()
    for line in raw.strip().splitlines():
        if line.upper().startswith("INTENT:"):
            v = line.split(":",1)[1].strip().lower()
            intent = v if v in _INTENTS else "other"
        elif line.upper().startswith("REPLY:"):
            reply = line.split(":",1)[1].strip()
    return intent, reply

# ── API call — direct anthropic client ────────────────────────────
def _api(messages, retries=2, delay=1.5):
    for i in range(retries+1):
        try:
            r = client.messages.create(
                model      = MODEL_NAME,
                max_tokens = 200,
                temperature= 0.3,
                system     = _SYS,
                tools      = _TOOLS,
                tool_choice= {"type":"auto"},
                messages   = messages
            )
            _track(r.usage)
            return r
        except anthropic.RateLimitError:
            log.warning(f"rate limit retry {i+1}"); time.sleep(delay)
        except anthropic.APIConnectionError:
            log.error(f"conn err retry {i+1}")
            if i < retries: time.sleep(delay)
        except Exception as e:
            log.error(f"api err: {e}"); break
    return None

# ── Main public function ───────────────────────────────────────────
def ask_claude(message, hint, history=[]):
    trimmed = [{"role":m["role"],"content":m["content"][:120]} for m in history[-6:]]
    msgs = [*trimmed, {"role":"user","content":f"MSG:{message}\nHINT:{hint}"}]

    r = _api(msgs)
    if not r: return _parse(_FALLBACK)

    log.info(f"stop_reason={r.stop_reason} blocks={[b.type for b in r.content]}")

    if r.stop_reason == "tool_use":
        tb     = next(b for b in r.content if b.type == "tool_use")
        result = get_institute_info(
            intent  = tb.input.get("intent", hint),
            course  = tb.input.get("course", "combined"),
            message = message
        )
        log.info(f"tool={tb.name} intent={tb.input.get('intent')} | {result[:60]}")

        f = _api([*msgs,
                  {"role":"assistant","content": r.content},
                  {"role":"user","content":[{
                      "type":"tool_result",
                      "tool_use_id": tb.id,
                      "content": result
                  }]}])
        if not f: return _parse(_FALLBACK)
        txt = next((b for b in f.content if b.type=="text"), None)
        return _parse(txt.text) if txt else _parse(_FALLBACK)

    txt = next((b for b in r.content if b.type=="text"), None)
    return _parse(txt.text) if txt else _parse(_FALLBACK)
