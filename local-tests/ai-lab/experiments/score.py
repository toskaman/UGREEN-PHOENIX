"""Pipeline scorer: verify + aggregate (+escalations) over transcripts.

Usage (from repo root):
  python local-tests/ai-lab/experiments/score.py --tag TAG --dataset DS
      [--cases c1,c2] [--delta priors.json]
Prints per-case verdict vs gold and the total. Exit 1 on any mismatch.
priors.json (optional): {case: [{subject, path}], ...} for delta states.
"""

import argparse
import glob
import json
import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

from datasets import extset, trackb
from evaluators import aggregate as agg
from evaluators import delta as delta_mod
from evaluators import verify as ver

TRANSCRIPTS = AI_LAB / "reports" / "transcripts"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--dataset", required=True, choices=["trackb", "ext"])
    ap.add_argument("--cases", default=None)
    ap.add_argument("--delta", default=None)
    args = ap.parse_args()
    ds = trackb if args.dataset == "trackb" else extset
    raw = ds.labels()
    labels = {k: v for k, v in raw.items() if not k.startswith("_")}
    priors = json.loads(Path(args.delta).read_text(encoding="utf-8")) \
        if args.delta else {}
    want = args.cases.split(",") if args.cases else sorted(labels)
    n = p = 0
    for case in want:
        tpath = sorted(TRANSCRIPTS.glob(f"{args.tag}_*_{case}.json"))
        if not tpath:
            print(f"{case}: NO TRANSCRIPT")
            continue
        d = json.loads(tpath[0].read_text(encoding="utf-8"))
        v = ver.verify(case, d["response"], dataset=args.dataset)
        tsv = v["tsv"]
        for epath in sorted(TRANSCRIPTS.glob(f"{args.tag}-esc_*_{case}.json")):
            e = json.loads(epath.read_text(encoding="utf-8"))
            tsv = ver.merge_rowfix(case, tsv, e["rowfix_lines"],
                                   dataset=args.dataset,
                                   base_unverified=v["unverified"])
        known = ds.known_files(case, raw)
        r = agg.aggregate(tsv, known=known)
        ok = r["verdict"] == labels[case]["verdict"]
        n += 1
        p += ok
        extra = ""
        if case in priors:
            dt = delta_mod.compute("DOCUMENTARY BLOCKER IDENTIFIED",
                                   priors[case], r)
            extra = f" delta={dt['deltas'][0]['state']}"
        print(f"{case}: {r['verdict']} | gold: {labels[case]['verdict']} | "
              f"{'PASS' if ok else 'FAIL'}{extra}")
    print(f"{args.tag}: {p}/{n}")
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main())
