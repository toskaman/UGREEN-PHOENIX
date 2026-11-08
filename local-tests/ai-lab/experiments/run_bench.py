"""Benchmark runner: model x Track B cases with ledger gating.

- Pre-authorizes every request against the budget ledger (worst case).
- Verifies returned model identity; mismatches are rejected from results.
- finish_reason == 'length' marks a case TRUNCATED (never a valid score).
- Transcripts carry request id, usage, latency, identity proof. No keys.
- Resume: existing transcripts are skipped unless --overwrite.
Usage (from repo root):
  python local-tests/ai-lab/experiments/run_bench.py --model MODEL
      [--cases tb1,tb3] [--tag NAME] [--max-out N] [--overwrite]
      [--prompt PATH] [--reasoning-budget N]
"""

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

import budget as budget_mod
import call as call_mod
import config
from datasets import extset, trackb
from evaluators import redact as redact_mod
from evaluators import verdict as verdict_mod
from providers import ollama, vultr

LEDGER = AI_LAB / "reports" / "ledger.jsonl"
TRANSCRIPTS = AI_LAB / "reports" / "transcripts"


def call_model(model: str, full_prompt: str, max_out: int,
               reasoning_budget: int | None, ledger, req_id: str,
               case: str, tag: str) -> dict:
    """Paid models go through the single ledger-gated accounting path
    (reserve -> attempts -> one terminal); local models stay direct."""
    spec = config.MODELS[model]
    if spec["provider"] == "vultr":
        messages = [{"role": "user", "content": full_prompt}]
        return call_mod.paid_chat(
            model, messages, max_out, ledger, req_id, case, tag,
            len(full_prompt), reasoning_budget=reasoning_budget)
    return ollama.generate(model, full_prompt)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="trackb", choices=["trackb", "ext"])
    ap.add_argument("--cases", default=None)
    ap.add_argument("--tag", default="bench")
    ap.add_argument("--max-out", type=int, default=config.DEFAULT_MAX_OUT)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--prompt", default=None,
                    help="v1|v2|v3 prompt name or explicit path")
    ap.add_argument("--reasoning-budget", type=int, default=None)
    args = ap.parse_args()

    if args.model not in config.MODELS:
        print(f"unknown model: {args.model}")
        return 1
    ds = trackb if args.dataset == "trackb" else extset
    named = {"v1": trackb.ROOT / "prompt.md", "v2": AI_LAB / "prompts/v2.md",
             "v3": AI_LAB / "prompts/v3.md"}
    if args.prompt is None:
        prompt, phash = trackb.prompt_text(), trackb.prompt_sha()
    elif args.prompt in named:
        prompt = named[args.prompt].read_text(encoding="utf-8")
        phash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    else:
        prompt = Path(args.prompt).read_text(encoding="utf-8")
        phash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    labels = {k: v for k, v in ds.labels().items()
              if not k.startswith("_")}
    pricing = {m: (v["in_per_m"], v["out_per_m"])
               for m, v in config.MODELS.items()}
    ledger = budget_mod.Ledger(LEDGER, config.BUDGET_USD,
                               config.MAX_REQUESTS, pricing,
                               ttl_s=config.RESERVATION_TTL_S)
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    spec = config.MODELS[args.model]
    paid = spec["provider"] == "vultr"

    want = args.cases.split(",") if args.cases else sorted(labels)
    for case in want:
        case = case.strip()
        if case not in labels:
            print(f"{case}: UNKNOWN CASE, skipped")
            continue
        tpath = TRANSCRIPTS / \
            f"{args.tag}_{args.model.replace(':', '_')}_{case}.json"
        if tpath.exists() and not args.overwrite:
            if paid:
                # Resume cross-check: a transcript without a COMPLETED
                # ledger terminal is not proof of a paid call (ledger
                # may have been lost); fail closed, require --overwrite.
                try:
                    old = json.loads(tpath.read_text(encoding="utf-8"))
                    st = ledger.request_state(old.get("request_id", ""))
                except (OSError, ValueError):
                    st = None
                if not st or st.get("state") != "COMPLETED":
                    print(f"{case}: transcript lacks a COMPLETED "
                          f"ledger terminal, refusing to skip "
                          f"(pass --overwrite to re-spend explicitly)")
                    continue
            print(f"{case}: transcript exists, skipped")
            continue
        full = prompt + "\n" + ds.case_input(case, ds.labels())
        rid = call_mod.deterministic_req_id(
            args.tag, args.model, case, phash, str(args.max_out))
        if paid and args.overwrite:
            # Explicit, auditable re-spend under a fresh request id.
            rid = f"{rid}-o{uuid.uuid4().hex[:8]}"
        try:
            res = call_model(args.model, full, args.max_out,
                             args.reasoning_budget, ledger, rid, case,
                             args.tag)
        except budget_mod.BudgetExceeded as exc:
            print(f"{case}: BUDGET REFUSED {exc}")
            return 1
        except vultr.VultrAuthError as exc:
            print(f"{case}: AUTH REFUSED {str(exc)[:200]} (aborting)")
            return 1
        except budget_mod.ReservationTerminal as exc:
            # COMPLETED in ledger but transcript missing (crash between
            # record and transcript write): the response is lost and the
            # money is spent; only an explicit --overwrite re-spends.
            print(f"{case}: LEDGER TERMINAL {exc} (pass --overwrite "
                  f"to re-spend explicitly)")
            continue
        except Exception as exc:  # noqa: BLE001 - runner reports, not crash
            print(f"{case}: ERROR {str(exc)[:200]}")
            continue
        ok = res["identity_ok"] and res["finish_reason"] != "length"
        status = "ok" if ok else (
            "mismatch" if not res["identity_ok"] else "truncated")
        cost = budget_mod.Ledger.actual_cost(
            args.model, res["prompt_tokens"], res["completion_tokens"],
            pricing) if paid else 0.0
        tpath.write_text(json.dumps({
            "request_id": rid, "model": args.model,
            "model_returned": res["model_returned"],
            "identity_ok": res["identity_ok"], "status": status,
            "case": case, "tag": args.tag, "prompt_sha": phash,
            "max_out": args.max_out,
            "reasoning_budget": args.reasoning_budget,
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "reasoning_tokens": res["reasoning_tokens"],
            "finish_reason": res["finish_reason"],
            "latency_s": res["latency_s"], "cost_usd": cost,
            "server_id": res.get("request_id", "") if paid else "",
            "ledger_state": res.get("ledger_state", "") if paid else "",
            "attempts": len(res.get("attempts", [])) if paid else 1,
            "verdict_line": verdict_mod.parse_verdict(res["text"]),
            "response": redact_mod.redact(res["text"])}, indent=2),
            encoding="utf-8")
        print(f"{case}: {verdict_mod.parse_verdict(res['text'])} "
              f"[{status}] ({res['latency_s']}s, ${cost:.6f})", flush=True)
    spent, held, n, corrupt = ledger.totals()
    print(f"ledger: ${spent:.6f} spent, ${held:.6f} held, {n} requests, "
          f"{corrupt} corrupt lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
