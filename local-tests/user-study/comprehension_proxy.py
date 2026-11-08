"""Synthetic comprehension proxy (NOT a user study).

Checks deterministic readability properties of §8 plain-language
sentences and §7 planner lines across the 8 frozen corpora: length
caps, jargon scan, required safety elements, marker discipline.
Measures text properties only — human understanding needs the real
(NOT RUN) study. Exit 0 when all properties hold.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import harness

JARGON = ["orchestration", "DAG", "embedding", "tokens", "inference",
          "namespace", "idempotent", "heuristic", "stochastic",
          "serialization", "normalization"]
REQUIRED = {
    "DOCUMENTARY BLOCKER IDENTIFIED": "do not assume",
    "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES":
        "not a tested restore",
    "INSUFFICIENT EVIDENCE": "no conclusion is possible yet",
}
CORPORA = ["core-a", "core-b", "core-c", "core-d", "edge", "edge-2",
           "edge-3", "scale"]
FAIL = []


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def main():
    for verdict, plain in harness.PLAIN_VERDICT.items():
        words = plain.split()
        check(f"plain[{verdict}]: <=40 words", len(words) <= 40,
              f"{len(words)} words")
        check(f"plain[{verdict}]: safety element",
              REQUIRED[verdict] in plain, plain)
        hits = [j for j in JARGON if j.lower() in plain.lower()]
        check(f"plain[{verdict}]: no jargon", not hits, str(hits))
    for corpus in CORPORA:
        res = harness.run(ROOT / "corpus" / corpus)
        sec7 = res["report"].split("## 7. Next steps")[1].split("## 8.")[0]
        acts = [ln for ln in sec7.splitlines() if ln.startswith("- P")]
        for ln in acts:
            check(f"{corpus}: action <=60 words",
                  len(ln.split()) <= 60, ln[:80])
            for key in ("(why: ", "evidence: ", "resolved-if: ",
                        "authorization: "):
                check(f"{corpus}: action has {key.strip()}",
                      key in ln, ln[:80])
            hits = [j for j in JARGON if j.lower() in ln.lower()]
            check(f"{corpus}: action no jargon", not hits, str(hits))
        if acts:
            check(f"{corpus}: FIRST CHECK exactly once",
                  sec7.count("[FIRST CHECK]") == 1, sec7[:120])
            check(f"{corpus}: residual present",
                  "- Regardless of results:" in sec7)
        else:
            check(f"{corpus}: empty §7 says none", "- none" in sec7)
    if FAIL:
        print(f"\n{len(FAIL)} PROXY FAILURES")
        sys.exit(1)
    print("\ncomprehension proxy OK (text properties only, NOT a user study)")


if __name__ == "__main__":
    main()
