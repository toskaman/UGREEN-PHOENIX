"""Beta planner trial round 3 (micro): multi-item FIRST CHECK placement.

core-d has 2 actionable items. Post-</think> scorer. Ship criteria:
exact line count, all cites valid, no drift, [FIRST CHECK] exactly
once on the first line. 2 calls (14B + 9B)."""

import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ai-lab"))

from providers.ollama import generate  # noqa: E402

MODELS = ["qwen2.5-coder-14b-opt:latest", "qwythos-9b-abliterated:optimized"]
EVIDENCE = ("- config/missing.yaml: NOT FOUND IN SCOPE (required by "
            "docs/deployment-guide.md:5) — bounded scope search returned "
            "no confirmed file.\n"
            "- runtime: CONFLICTING (required by "
            "docs/deployment-guide.md:6) — observed config/app.yaml:2 "
            "(2.9.0) contradicts required >= 3.0.")
CITES = ["docs/deployment-guide.md:5", "docs/deployment-guide.md:6",
         "config/app.yaml:2"]
BASES = ["missing.yaml", "runtime"]
BANNED = ["update the", "upgrade the", "modify ", "similar", "rename",
          "create ", "delete ", "edit "]


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    instr = ("Write 'Next steps' as an Evidence Gain Planner. There are "
             "exactly 2 evidence items above: write exactly 2 action "
             "lines, one per item, no more, P1 blockers first. Put "
             "[FIRST CHECK] at the start of the first action line only. "
             "Every action line: `- P1: <action> (why: <which blocker it "
             "addresses>; evidence: <path:line cite>; resolved-if: <what "
             "observed result counts as resolved>; authorization: <note>)`. "
             "Actions must be verification checks only (re-observe, "
             "confirm, request access): never propose modifying files, "
             "updating versions, or searching for similar names; cite "
             "exact paths only. Close with a '- Regardless of results: "
             "<what stays unverified>' line. Use only the evidence above; "
             "invent nothing.")
    prompt = (f"Evidence:\n{EVIDENCE}\nVerdict: DOCUMENTARY BLOCKER "
              f"IDENTIFIED\n\n{instr}\nNext steps:")
    results = []
    for model in MODELS:
        r = generate(model, prompt)
        body = r["text"].split("</think>")[-1]
        lines = [ln.strip() for ln in body.splitlines()
                 if ln.strip().startswith("- P")]
        firsts = sum(1 for ln in lines if ln.startswith("- P1: [FIRST CHECK]")
                     or ln.startswith("- P2: [FIRST CHECK]"))
        ok = (r["finish_reason"] == "stop" and r["identity_ok"]
              and len(lines) == 2
              and all(any(c in ln for c in CITES) for ln in lines)
              and all(any(b in ln for b in BASES) for ln in lines)
              and not any(w in ln.lower()
                          for ln in lines for w in BANNED)
              and firsts == 1
              and "- Regardless of results:" in body)
        results.append(ok)
        print(f"{model.split(':')[0]} | lines={len(lines)} firsts={firsts} "
              f"resid={'- Regardless of results:' in body} "
              f"PASS={ok} ({r['latency_s']}s)")
        (HERE / "ai-lab" / "reports" /
         f"beta-trial3-{stamp}-{model.split(':')[0]}.txt"
         ).write_text(f"MODEL: {model}\nPROMPT:\n{prompt}\n\nRESPONSE:\n"
                      f"{r['text']}\n", encoding="utf-8")
    print(f"\n{sum(results)}/{len(results)} round-3 cells passed")


if __name__ == "__main__":
    main()
