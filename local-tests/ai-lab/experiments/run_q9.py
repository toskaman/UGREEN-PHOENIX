"""Q9 conditional-transfer runner: 12 fresh probes x N models.

Each probe presents one gated/XOR/boolean requirement plus observed
evidence; the model must emit one VERDICT line. Scoring is strict
string match on the verdict token. Transcripts land next to the
other ai-lab transcripts for audit.

Usage:
  python local-tests/ai-lab/experiments/run_q9.py \
      --models qwen2.5-coder-14b-opt:latest,qwythos-9b-abliterated:optimized
"""

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

AI_LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AI_LAB))
from providers import ollama  # noqa: E402

Q9 = AI_LAB / "datasets" / "q9_transfer"
OUT = AI_LAB / "reports" / "transcripts"

TOK = re.compile(r"\b(SATISFIED|VIOLATED|UNKNOWN)\b")


def parse_verdict(text: str) -> str:
    """The model's concluded verdict: an explicit VERDICT: line wins,
    else the LAST verdict token (conclusions come after reasoning;
    first-substring matching misreads 'not SATISFIED ... UNKNOWN')."""
    up = text.upper()
    m = re.search(r"^VERDICT:\s*(SATISFIED|VIOLATED|UNKNOWN)\b",
                  up, re.M)
    if m:
        return m.group(1)
    found = TOK.findall(up)
    return found[-1] if found else "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--tag", default="q9")
    ap.add_argument("--num-ctx", type=int, default=8192)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    prompt = (Q9 / "prompt.md").read_text(encoding="utf-8")
    phash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    cases = json.loads((Q9 / "cases.json").read_text(encoding="utf-8"))["cases"]

    summary = {}
    for model in [m.strip() for m in args.models.split(",")]:
        correct, total, lat = 0, 0, 0.0
        for c in cases:
            total += 1
            tpath = OUT / (f"{args.tag}_{model.replace(':', '_')}"
                           f"_{c['id']}.json")
            if tpath.exists() and not args.overwrite:
                d = json.loads(tpath.read_text(encoding="utf-8"))
                got = parse_verdict(d.get("response", ""))
                if got != d.get("verdict"):
                    d["verdict"] = got  # re-parse saved response
                    tpath.write_text(json.dumps(d, indent=2),
                                     encoding="utf-8")
            else:
                full = (prompt + "\nRequirement: " + c["requirement"]
                        + "\nObserved: " + c["observed"] + "\nVERDICT:")
                t0 = time.perf_counter()
                res = ollama.generate(model, full, num_ctx=args.num_ctx)
                lat += time.perf_counter() - t0
                text = res["text"]
                got = parse_verdict(text)
                tpath.write_text(json.dumps({
                    "model": model,
                    "model_returned": res["model_returned"],
                    "identity_ok": res["identity_ok"],
                    "case": c["id"], "tag": args.tag,
                    "prompt_sha": phash, "num_ctx": args.num_ctx,
                    "finish_reason": res["finish_reason"],
                    "latency_s": res["latency_s"],
                    "expected": c["expected"], "verdict": got,
                    "response": text}, indent=2), encoding="utf-8")
            mark = "ok" if got == c["expected"] else "MISS"
            if got == c["expected"]:
                correct += 1
            print(f"{model} {c['id']}: got {got}, want "
                  f"{c['expected']} [{mark}]", flush=True)
        summary[model] = f"{correct}/{total}"
        print(f"{model}: {correct}/{total} "
              f"({lat:.1f}s inference this run)")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
