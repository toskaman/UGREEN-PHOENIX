"""Local Ollama provider ($0). Same result shape as vultr.chat()."""

import json
import time
import urllib.request


def generate(model: str, prompt: str, num_ctx: int = 8192,
             timeout: int = 900) -> dict:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "num_ctx": num_ctx}}
                      ).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                 data=body,
                                 headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    returned = data.get("model", "")
    done_reason = (data.get("done_reason") or "").lower()
    if done_reason == "length":
        finish = "length"  # context/generation cap hit: never valid
    elif data.get("done"):
        finish = "stop"
    else:
        finish = "unknown"
    return {
        "request_id": f"ollama-{int(start)}",
        "model_requested": model,
        "model_returned": returned,
        "identity_ok": bool(returned) and returned == model,
        "text": data.get("response", ""),
        "reasoning": "",
        "finish_reason": finish,
        "native_finish_reason": "",
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "completion_tokens": data.get("eval_count", 0),
        "reasoning_tokens": 0,
        "cached_tokens": 0,
        "latency_s": round(time.perf_counter() - start, 2),
    }
