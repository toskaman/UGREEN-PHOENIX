"""Single paid-call accounting path (Vultr Serverless Inference).

All paid inference funnels through paid_chat(): reserve -> attempts ->
one terminal ledger state. No caller may touch the network for a paid
model without going through here (this closes the escalate.py bypass).

Retry policy follows the Vultr errors doc (checked 2026-11-08):
- 429: wait Retry-After seconds, then retry
- 500: retry at most ONCE
- 502/503/504: exponential backoff (1s, 2s, ...)
- 401/400/404/connection-refused: no retry, FAILED_NO_CHARGE
- timeout / 5xx-exhausted / error-payload-without-usage: UNKNOWN_CHARGE

Terminal mapping is conservative: anything that may have billed the
provider holds the full estimate until reconcile() sees statement
evidence. Billed-but-rejected calls (identity mismatch, truncation)
are COMPLETED with actual cost: real spend is real spend.
"""

import hashlib
import time

import budget as budget_mod
import config
from providers import vultr

# Refused before generation: no charge. (Vultr docs do not state chat
# billing per status; 429 rate_limit_exceeded / 400 unsupported param /
# 404 unknown model are refusals by construction. Documented assumption.)
NO_CHARGE_STATUS = (400, 401, 404, 422, "connection")
RETRY_STATUS = (429, 500, 502, 503, 504)


def deterministic_req_id(*parts: str) -> str:
    blob = "\x00".join(parts).encode("utf-8")
    return "q-" + hashlib.sha1(blob).hexdigest()[:16]


def _wait(seconds: float, sleep) -> None:
    sleep(min(seconds, 120.0))


def paid_chat(model: str, messages: list, max_out: int,
              ledger: budget_mod.Ledger, req_id: str, case: str,
              tag: str, prompt_chars: int, timeout: int | None = None,
              temperature: float = 0.0, reasoning_budget: int | None = None,
              sleep=time.sleep, transport=None) -> dict:
    """Reserve, call with bounded retries, record exactly one terminal.

    transport: injectable (model, messages, max_out, ...) -> result dict
    for offline tests; defaults to vultr.chat. Raises BudgetExceeded,
    ReservationTerminal, VultrAuthError, or the terminal VultrError.
    """
    timeout = config.DEFAULT_TIMEOUT_S if timeout is None else timeout
    transport = transport or vultr.chat
    try:
        ledger.reserve(req_id, model, case, tag, prompt_chars, max_out)
    except budget_mod.ReservationTerminal as exc:
        if exc.state == "EXPIRED":
            # Re-reserve once under a superseding RESERVED line.
            ledger.reserve(req_id + "-r", model, case, tag, prompt_chars,
                           max_out)
            req_id = req_id + "-r"
        else:
            raise
    attempts: list[dict] = []
    tries_500 = 0
    last: vultr.VultrError | None = None
    max_attempts = config.MAX_RETRIES + 1
    for n in range(1, max_attempts + 1):
        try:
            res = transport(model, messages, max_out=max_out,
                            temperature=temperature,
                            reasoning_budget=reasoning_budget,
                            timeout=timeout)
        except vultr.VultrAuthError:
            ledger.fail_no_charge(req_id, note="auth refused")
            raise
        except vultr.VultrError as exc:
            last = exc
            entry = {"n": n, "http": exc.status,
                     "err": str(exc)[:200]}
            if exc.retry_after:
                entry["retry_after"] = exc.retry_after
            attempts.append(entry)
            ledger.note_attempt(req_id, list(attempts))
            if exc.status == 429 and n < max_attempts:
                _wait(float(exc.retry_after or 5), sleep)
                continue
            if exc.status in (502, 503, 504) and n < max_attempts:
                _wait(2.0 ** (n - 1), sleep)
                continue
            if exc.status == 500 and tries_500 == 0 \
                    and n < max_attempts:
                tries_500 += 1
                _wait(2.0, sleep)
                continue
            break
        # HTTP 200 with a usable payload.
        attempts.append({"n": n, "http": 200,
                         "prompt_tok": res["prompt_tokens"],
                         "completion_tok": res["completion_tokens"],
                         "server_id": res.get("request_id", "")})
        ledger.note_attempt(req_id, list(attempts))
        ok = res["identity_ok"] and res["finish_reason"] != "length"
        status = "ok" if ok else (
            "mismatch" if not res["identity_ok"] else "truncated")
        actual = budget_mod.Ledger.actual_cost(
            model, res["prompt_tokens"], res["completion_tokens"],
            ledger.pricing)
        ledger.complete(req_id, actual, identity_ok=res["identity_ok"],
                        finish_reason=res["finish_reason"], status=status,
                        server_id=res.get("request_id", ""),
                        attempts=list(attempts))
        res["attempts"] = list(attempts)
        res["ledger_state"] = "COMPLETED"
        return res
    # Exhausted retries or hit a non-retryable error.
    assert last is not None
    if last.status in NO_CHARGE_STATUS:
        attempts[-1]["no_charge"] = True
        ledger.note_attempt(req_id, list(attempts))
        ledger.fail_no_charge(req_id, note=f"refused: {last.status}")
        raise last
    if last.usage and (last.usage.get("prompt_tokens") or
                       last.usage.get("completion_tokens")):
        # Error payload that still reports token consumption: billed.
        actual = budget_mod.Ledger.actual_cost(
            model, last.usage.get("prompt_tokens", 0),
            last.usage.get("completion_tokens", 0), ledger.pricing)
        ledger.complete(req_id, actual, identity_ok=False,
                        finish_reason="error", status="error-billed",
                        server_id="", attempts=list(attempts),
                        note="error payload with usage")
        raise last
    ledger.fail_unknown(req_id, note=f"ambiguous: {last.status}")
    raise last
