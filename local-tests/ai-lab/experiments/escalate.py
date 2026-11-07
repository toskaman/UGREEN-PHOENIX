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

import config
from datasets import extset, trackb
from evaluators import aggregate as agg
from evaluators import verify as ver
from providers import ollama, vultr

TRANSCRIPTS = AI_LAB / "reports" / "transcripts"


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
    extra = []
    for subj, path in v["unverified"]:
        full = (rowfix + path + f" (requirement: {subj})\n\n"
                + ds.case_input(args.case, labels))
        spec = config.MODELS[args.model]
        if spec["provider"] == "vultr":
            res = vultr.chat(args.model, [{"role": "user", "content": full}],
                             max_out=512, temperature=0.0)
            text = res["text"]
        else:
            res = ollama.generate(args.model, full)
            text = res["text"]
        line = next((l for l in text.strip().splitlines()
                     if "|" in l or "\t" in l), "")
        print(f"rowfix {subj}: {line[:120]}")
        if line:
            extra.append(line)
    merged = v["tsv"] + "\n" + "\n".join(extra)
    r = agg.aggregate(merged)
    gold = labels[args.case]["verdict"]
    print(f"{args.case} escalated -> {r['verdict']} | gold: {gold} | "
          f"{'PASS' if r['verdict'] == gold else 'FAIL'}")
    out = TRANSCRIPTS / \
        f"{args.tag}-esc_{args.model.replace(':', '_')}_{args.case}.json"
    out.write_text(json.dumps({"base": base.name, "unverified": v["unverified"],
                               "rowfix_lines": extra,
                               "verdict": r["verdict"],
                               "findings": r["findings"]}, indent=2),
                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
