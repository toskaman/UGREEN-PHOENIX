"""One-shot escalation: re-transcribe unverified rows, then aggregate.

Usage (from repo root):
  python local-tests/ai-lab/experiments/escalate.py --model M --dataset D --case C --tag T
Reads the base transcript <T>_<M>_<C>.json, verifies rows, calls rowfix
for each unverified subject, re-aggregates, writes <T>-esc transcript.
"""
import argparse
import json
import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

import budget as budget_mod
import call as call_mod
import config
from datasets import extset, trackb
from evaluators import aggregate as agg
from evaluators import redact as redact_mod
from evaluators import verify as ver
from providers import ollama

TRANSCRIPTS = AI_LAB / "reports" / "transcripts"
LEDGER = AI_LAB / "reports" / "ledger.jsonl"


def _safe_span(text: str, limit: int = 120) -> str:
    """Single-line printable span for prompt interpolation. Model-
    derived paths/subjects are never spliced raw into a prompt."""
    one = " ".join(str(text).split())
    one = "".join(c for c in one if c.isprintable())
    return one[:limit] if one else "(unverified source)"


def _allowlisted(path: str, known: dict) -> str:
    if path in known:
        return path
    return "(unverified source)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="trackb")
    ap.add_argument("--case", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    ds = trackb if args.dataset == "trackb" else extset
    labels = ds.labels()
    base = TRANSCRIPTS / \
        f"{args.tag}_{args.model.replace(':', '_')}_{args.case}.json"
    d = json.loads(base.read_text(encoding="utf-8"))
    v = ver.verify(args.case, d["response"], dataset=args.dataset)
    if not v["unverified"]:
        print("nothing to escalate")
        return 0
    rowfix = (AI_LAB / "prompts/rowfix.md").read_text(encoding="utf-8")
    spec = config.MODELS[args.model]
    paid = spec["provider"] == "vultr"
    ledger = None
    if paid:
        pricing = {m: (v["in_per_m"], v["out_per_m"])
                   for m, v in config.MODELS.items()}
        ledger = budget_mod.Ledger(LEDGER, config.BUDGET_USD,
                                   config.MAX_REQUESTS, pricing,
                                   ttl_s=config.RESERVATION_TTL_S)
    known = ds.known_files(args.case, labels)
    extra = []
    for subj, path in v["unverified"]:
        safe_subj = _safe_span(subj)
        safe_path = _safe_span(_allowlisted(path, known))
        full = (rowfix + safe_path + f" (requirement: {safe_subj})\n\n"
                + ds.case_input(args.case, labels))
        if paid:
            rid = call_mod.deterministic_req_id(
                args.tag + "-esc", args.model, args.case, safe_subj,
                safe_path)
            try:
                res = call_mod.paid_chat(
                    args.model, [{"role": "user", "content": full}], 512,
                    ledger, rid, args.case, args.tag + "-esc",
                    len(full))
            except budget_mod.BudgetExceeded as exc:
                print(f"rowfix {safe_subj}: BUDGET REFUSED {exc}")
                return 1
            text = res["text"]
        else:
            res = ollama.generate(args.model, full)
            text = res["text"]
        line = next((l for l in text.strip().splitlines()
                     if "|" in l or "\t" in l), "")
        print(f"rowfix {subj}: {line[:120]}")
        if line:
            extra.append(line)
    merged = ver.merge_rowfix(args.case, v["tsv"], extra,
                                dataset=args.dataset,
                                base_unverified=v["unverified"])
    known = ds.known_files(args.case, labels)
    r = agg.aggregate(merged, known=known,
                      truncated_docs=ver.truncated_docs(
                          args.case, args.dataset))
    gold = labels[args.case]["verdict"]
    print(f"{args.case} escalated -> {r['verdict']} | gold: {gold} | "
          f"{'PASS' if r['verdict'] == gold else 'FAIL'}")
    out = TRANSCRIPTS / \
        f"{args.tag}-esc_{args.model.replace(':', '_')}_{args.case}.json"
    out.write_text(json.dumps({"base": base.name, "unverified": v["unverified"],
                               "rowfix_lines": [redact_mod.redact(line)
                                                for line in extra],
                               "verdict": r["verdict"],
                               "findings": r["findings"]}, indent=2),
                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
