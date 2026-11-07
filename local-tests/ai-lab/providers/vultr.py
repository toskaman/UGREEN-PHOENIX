"""Vultr Serverless Inference provider (OpenRouter-shaped chat API).

Security contract:
- Key comes ONLY from env (VULTR_INFERENCE_API_KEY, else VULTR_API_KEY).
- The key is never printed, logged, or included in any exception text.
- Every response's returned model id is checked against the request;
  a silent substitution rejects the run (never silently accepted).
- Reasoning arrives in `reasoning` (never `reasoning_content`); usage
  carries prompt/completion details incl. reasoning tokens.
"""

import json
import os
import time
import urllib.request

from config import BASE_URL


class VultrAuthError(RuntimeError):
    pass


class VultrError(RuntimeError):
    pass


def _key() -> str:
    key = os.environ.get("VULTR_INFERENCE_API_KEY") or \
        os.environ.get("VULTR_API_KEY", "")
    if not key:
        raise VultrAuthError("no Vultr key in env "
                             "(VULTR_INFERENCE_API_KEY/VULTR_API_KEY)")
    return key


def _scrub(text: str, key: str) -> str:
    return text.replace(key, "[REDACTED]")


def identities_match(requested: str, returned: str) -> bool:
    """Exact match, tolerating only the documented '-normalize' suffix."""
    if not returned:
        return False
    if returned == requested:
        return True
    return returned == requested + "-normalize" or \
        requested == returned + "-normalize"


def chat(model: str, messages: list, max_out: int, temperature: float = 0.0,
         reasoning_budget: int | None = None,
         timeout: int = 180) -> dict:
    key = _key()
    body: dict = {"model": model, "messages": messages,
                  "temperature": temperature,
                  "max_completion_tokens": max_out}
    if reasoning_budget is not None:
        body["reasoning"] = {"max_tokens": reasoning_budget}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + "/chat/completions", data=data,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except Exception as exc:  # noqa: BLE001 - must scrub, then classify
        msg = _scrub(str(exc), key)
        if "401" in msg:
            raise VultrAuthError("401 from inference API: " + msg[:200])
        raise VultrError(msg[:300])
    secs = time.perf_counter() - start
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise VultrError(f"HTTP {status}: non-JSON body ({len(raw)} chars)")
    if "error" in payload:
        raise VultrError(f"HTTP {status}: "
                         f"{json.dumps(payload['error'])[:300]}")
    choice = (payload.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    usage = payload.get("usage") or {}
    returned = payload.get("model", "")
    return {
        "request_id": payload.get("id", ""),
        "model_requested": model,
        "model_returned": returned,
        "identity_ok": identities_match(model, returned),
        "text": msg.get("content") or "",
        "reasoning": msg.get("reasoning") or "",
        "finish_reason": choice.get("finish_reason", ""),
        "native_finish_reason": choice.get("native_finish_reason", ""),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "reasoning_tokens": (usage.get("completion_tokens_details") or {})
        .get("reasoning_tokens", 0),
        "cached_tokens": (usage.get("prompt_tokens_details") or {})
        .get("cached_tokens", 0),
        "latency_s": round(secs, 2),
    }
