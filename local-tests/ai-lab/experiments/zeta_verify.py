"""Zeta verify: does an in-context verdict checklist fix 14B abstention?

Single cell (14B, edge, full + checklist). The checklist is the
candidate SKILL step-5 addition; ship it only if this cell passes.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ai-lab"))

from providers.ollama import generate  # noqa: E402

FULL = """You are the report assembler. Use ONLY the upstream results below.
Write exactly these sections: Scenario; Coverage; Requirements; Evidence
table (REQUIREMENT, SOURCE, STATUS, VERSION, UNCERTAINTY); Priority
blockers; Contradictions; Next steps; Verdict.
Label every dependency FOUND, CONFLICTING, NOT FOUND IN SCOPE,
INACCESSIBLE, or UNKNOWN. Translate verification results: PRESENT feeds
the row (FOUND only when the observed file satisfies the extracted
constraint, else CONFLICTING); ABSENT becomes NOT FOUND IN SCOPE;
INACCESSIBLE stays INACCESSIBLE; UNRESOLVED becomes UNKNOWN; OUT OF
SCOPE and UNSAFE become UNKNOWN, never a clear label.
Verdict checklist (mechanical, no judgment): list the worst label
present. Any CONFLICTING or NOT FOUND IN SCOPE verdicts DOCUMENTARY
BLOCKER IDENTIFIED. Else any UNKNOWN or INACCESSIBLE verdicts
INSUFFICIENT EVIDENCE. Else the scope is clear. A clear verdict next
to any UNKNOWN or INACCESSIBLE row is forbidden. Zero cited rows means
INSUFFICIENT EVIDENCE, never clear. Echo every upstream coverage note
and failure verbatim; never invent counts. Next steps: exactly one
action per evidence row; mark the first with [FIRST CHECK]; each
states why, exact cite, resolved-if, authorization; close with
Regardless-of-results. Never produce a recovery percentage, never
declare anything restored, never invent a path. End with the exact
verdict line."""

UPSTREAM = ("Discovery: reviewed guide.md (EXTRACTION TRUNCATED "
            "at line 3), skipped data.bin (unsupported suffix). "
            "Extraction: 1 row, cache/key.txt required by "
            "guide.md:1, truncated source. Verification: "
            "UNRESOLVED (source incomplete).")


def main():
    r = generate("qwen2.5-coder-14b-opt:latest",
                 f"Upstream results:\n{UPSTREAM}\n\n{FULL}")
    body = r["text"].split("</think>")[-1]
    ok = ("INSUFFICIENT EVIDENCE" in body
          and "NO DOCUMENTARY BLOCKER" not in body
          and r["finish_reason"] == "stop")
    print(f"finish={r['finish_reason']} abstain_ok={ok} "
          f"({r['latency_s']}s)")
    print("--- response tail ---")
    print("\n".join(body.strip().splitlines()[-6:]))
    (HERE / "ai-lab" / "reports" / "zeta-verify-14b-edge.txt").write_text(
        f"RESPONSE:\n{r['text']}\n", encoding="utf-8")
    print(f"\nCHECKLIST CELL: {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
