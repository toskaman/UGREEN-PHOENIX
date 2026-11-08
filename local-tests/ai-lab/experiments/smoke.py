"""Stage 1 smoke test: 1 tiny paid call per Vultr model.

Verifies auth, request/response shape, usage fields, model-identity
echo, and ledger accounting for ~$0.001 total. Fails loudly on 401
(no retries), identity mismatch, or missing usage.
Usage (from repo root): python local-tests/ai-lab/experiments/smoke.py
"""

import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

import budget as budget_mod
import call as call_mod
import config
from providers import vultr

LEDGER = AI_LAB / "reports" / "ledger.jsonl"


def main() -> int:
    pricing = {m: (v["in_per_m"], v["out_per_m"])
               for m, v in config.MODELS.items()}
    ledger = budget_mod.Ledger(LEDGER, config.BUDGET_USD,
                               config.MAX_REQUESTS, pricing,
                               ttl_s=config.RESERVATION_TTL_S)
    spent, held, n, corrupt = ledger.totals()
    print(f"ledger: ${spent:.6f} spent, ${held:.6f} held, {n} requests")
    failures = 0
    for model, spec in config.MODELS.items():
        if spec["provider"] != "vultr":
            continue
        rid = f"smoke-{model}"
        messages = [{"role": "user", "content": "Reply with exactly: OK"}]
        prompt_chars = len(messages[0]["content"])
        try:
            res = call_mod.paid_chat(model, messages, 8, ledger, rid,
                                     "smoke", "smoke", prompt_chars)
        except budget_mod.BudgetExceeded as exc:
            print(f"{model}: BUDGET REFUSED {exc}")
            return 1
        except budget_mod.ReservationTerminal as exc:
            print(f"{model}: already smoked ({exc}), skipped")
            continue
        except vultr.VultrAuthError as exc:
            print(f"{model}: AUTH FAIL (no retry): {exc}")
            return 1
        except vultr.VultrError as exc:
            print(f"{model}: ERROR: {exc}")
            failures += 1
            continue
        cost = budget_mod.Ledger.actual_cost(
            model, res["prompt_tokens"], res["completion_tokens"], pricing)
        flag = "" if res["identity_ok"] else " IDENTITY-MISMATCH"
        print(f"{model}: ok text={res['text'].strip()[:20]!r} "
              f"in={res['prompt_tokens']} out={res['completion_tokens']} "
              f"reason={res['reasoning_tokens']} ${cost:.6f} "
              f"{res['latency_s']}s{flag}")
        if not res["identity_ok"]:
            failures += 1
    spent, held, n, corrupt = ledger.totals()
    print(f"ledger now: ${spent:.6f} spent, ${held:.6f} held, "
          f"{n} requests, {corrupt} corrupt lines")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
