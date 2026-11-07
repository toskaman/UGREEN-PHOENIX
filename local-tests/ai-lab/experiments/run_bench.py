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
import config
from datasets import extset, trackb
from evaluators import verdict as verdict_mod
from providers import ollama, vultr

LEDGER = AI_LAB / "reports" / "ledger.jsonl"
TRANSCRIPTS = AI_LAB / "reports" / "transcripts"


def call_model(model: str, full_prompt: str, max_out: int,
               reasoning_budget: int | None) -> dict:
    spec = config.MODELS[model]
    if spec["provider"] == "vultr":
        messages = [{"role": "user", "content": full_prompt}]
        last: Exception | None = None
        for _ in range(config.MAX_RETRIES + 1):
            try:
                return vultr.chat(model, messages, max_out=max_out,
                                  temperature=0.0,
                                  reasoning_budget=reasoning_budget)
            except vultr.VultrAuthError:
                raise
            except vultr.VultrError as exc:
                last = exc
                msg = str(exc)
                if "429" not in msg and "500" not in msg \
                        and "502" not in msg and "503" not in msg:
                    raise
        raise last  # type: ignore[misc]
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
                               config.MAX_REQUESTS, pricing)
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
            print(f"{case}: transcript exists, skipped")
            continue
        full = prompt + "\n" + ds.case_input(case, ds.labels())
        rid = f"{args.tag}-{uuid.uuid4().hex[:8]}"
        if paid:
            try:
                est = ledger.authorize(args.model, len(full), args.max_out)
            except budget_mod.BudgetExceeded as exc:
                print(f"{case}: BUDGET REFUSED {exc}")
                return 1
        else:
            est = 0.0
        try:
            res = call_model(args.model, full, args.max_out,
                             args.reasoning_budget)
        except Exception as exc:  # noqa: BLE001 - runner reports, not crash
            print(f"{case}: ERROR {str(exc)[:200]}")
            continue
        ok = res["identity_ok"] and res["finish_reason"] != "length"
        status = "ok" if ok else (
            "mismatch" if not res["identity_ok"] else "truncated")
        cost = budget_mod.Ledger.actual_cost(
            args.model, res["prompt_tokens"], res["completion_tokens"],
            pricing) if paid else 0.0
        if paid:
            ledger.record({"request_id": rid, "model": args.model,
                           "model_returned": res["model_returned"],
                           "identity_ok": res["identity_ok"],
                           "status": status, "case": case, "tag": args.tag,
                           "prompt_tokens": res["prompt_tokens"],
                           "completion_tokens": res["completion_tokens"],
                           "reasoning_tokens": res["reasoning_tokens"],
                           "finish_reason": res["finish_reason"],
                           "latency_s": res["latency_s"], "cost_usd": cost,
                           "est_max_usd": est})
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
            "verdict_line": verdict_mod.parse_verdict(res["text"]),
            "response": res["text"]}, indent=2), encoding="utf-8")
        print(f"{case}: {verdict_mod.parse_verdict(res['text'])} "
              f"[{status}] ({res['latency_s']}s, ${cost:.6f})", flush=True)
    spent, n = ledger.totals()
    print(f"ledger: ${spent:.6f} spent, {n} paid requests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
