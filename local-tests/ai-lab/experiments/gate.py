"""Offline Arch C gate: citation resolution + forbidden scan on transcripts.

Usage (from repo root):
  python local-tests/ai-lab/experiments/gate.py --tag v2 --model SUFFIX
"""
import argparse
import glob
import json
import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

from datasets import extset, trackb
from evaluators import verdict as verdict_mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", default="trackb", choices=["trackb", "ext"])
    args = ap.parse_args()
    ds = trackb if args.dataset == "trackb" else extset
    raw = ds.labels()
    labels = {k: v for k, v in raw.items() if not k.startswith("_")}
    gold = {c: labels[c]["verdict"] for c in labels}
    n = gate_pass = 0
    for f in sorted(glob.glob(str(AI_LAB / "reports/transcripts" /
                                 f"{args.tag}_{args.model}_*.json"))):
        d = json.load(open(f))
        case = d["case"]
        line = verdict_mod.parse_verdict(d["response"])
        cites = verdict_mod.check_citations(
            d["response"], ds.known_files(case, raw))
        forb = verdict_mod.scan_forbidden(d["response"])
        ok = (line == gold.get(case) and not cites["unresolved"]
              and not forb and d.get("status") == "ok")
        n += 1
        gate_pass += ok
        print(f"{case}: line={line} gold={gold.get(case)} "
              f"unresolved={cites['unresolved']} forbidden={forb} "
              f"-> {'GATE-PASS' if ok else 'gate-fail'}")
    print(f"arch-C gate: {gate_pass}/{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
