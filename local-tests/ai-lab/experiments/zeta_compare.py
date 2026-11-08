"""Zeta: full vs short report-assembly instruction on 9B + 14B.

Tests the knowledge-agent step in isolation: identical upstream
results (2 frozen cases: core-a BLOCKER, edge INSUFFICIENT), two
instruction variants. Scored: verdict correct, cites preserved, no
invented paths, verdict-line format, termination. Local Ollama ($0).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "ai-lab"))

from providers.ollama import generate  # noqa: E402

MODELS = ["qwen2.5-coder-14b-opt:latest", "qwythos-9b-abliterated:optimized"]

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
Verdict rule: any CONFLICTING or NOT FOUND IN SCOPE blocks
(DOCUMENTARY BLOCKER IDENTIFIED); else any UNKNOWN or INACCESSIBLE
abstains (INSUFFICIENT EVIDENCE); else clear (NO DOCUMENTARY BLOCKER
FOUND IN REVIEWED SOURCES). Zero cited rows means INSUFFICIENT
EVIDENCE, never clear. Echo every upstream coverage note and failure
verbatim; never invent counts. Next steps: exactly one action per
evidence row; mark the first with [FIRST CHECK]; each states why,
exact cite, resolved-if, authorization; close with Regardless-of-results.
Never produce a recovery percentage, never declare anything restored,
never invent a path. End with the exact verdict line."""

SHORT = """Assemble the report from ONLY the upstream results. Sections:
Scenario; Coverage; Requirements; Evidence table; Priority blockers;
Contradictions; Next steps; Verdict. Labels: FOUND, CONFLICTING,
NOT FOUND IN SCOPE, INACCESSIBLE, UNKNOWN. Map OUT OF SCOPE and
UNSAFE to UNKNOWN. Verdict: CONFLICTING/NOT FOUND blocks;
UNKNOWN/INACCESSIBLE abstains (INSUFFICIENT EVIDENCE); else clear.
Zero cited rows abstains. Echo coverage verbatim. Next steps: one
action per row with cite and resolved-if. No percentages, no restored
claims, no invented paths. End with the exact verdict line."""

CASES = {
    "core-a": {
        "upstream": ("Discovery: reviewed docs/deployment-guide.md, "
                     "app/main.py. Extraction: config/prod-config.yaml "
                     "required by docs/deployment-guide.md:5; app/main.py "
                     "required by docs/deployment-guide.md:2. "
                     "Verification: config/prod-config.yaml ABSENT "
                     "(bounded search, old-backup decoy rejected); "
                     "app/main.py PRESENT, satisfies no-version constraint."),
        "verdict": "DOCUMENTARY BLOCKER IDENTIFIED",
        "cites": ["docs/deployment-guide.md:5", "docs/deployment-guide.md:2"],
        "paths": ["config/prod-config.yaml", "app/main.py"],
    },
    "edge": {
        "upstream": ("Discovery: reviewed guide.md (EXTRACTION TRUNCATED "
                     "at line 3), skipped data.bin (unsupported suffix). "
                     "Extraction: 1 row, cache/key.txt required by "
                     "guide.md:1, truncated source. Verification: "
                     "UNRESOLVED (source incomplete)."),
        "verdict": "INSUFFICIENT EVIDENCE",
        "cites": ["guide.md:1"],
        "paths": ["cache/key.txt"],
    },
}


def score(text, case):
    body = text.split("</think>")[-1]
    data = CASES[case]
    verdict_ok = data["verdict"] in body
    cites_ok = all(c in body for c in data["cites"])
    invented = [w for w in ("/etc/", "/tmp/", "C:\\", "prod-config.yaml.bak")
                if w in body]
    fmt_ok = body.strip().splitlines()[-1].strip().startswith(
        ("DOCUMENTARY", "NO DOCUMENTARY", "INSUFFICIENT"))
    ok = verdict_ok and cites_ok and not invented
    return {"verdict_ok": verdict_ok, "cites_ok": cites_ok,
            "invented": invented, "format_last_line": fmt_ok, "pass": ok}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"full words: {len(FULL.split())}, short words: {len(SHORT.split())}")
    results = []
    for model in MODELS:
        for case, data in CASES.items():
            for variant, instr in (("full", FULL), ("short", SHORT)):
                prompt = (f"Upstream results:\n{data['upstream']}\n\n"
                          f"{instr}")
                r = generate(model, prompt)
                s = score(r["text"], case)
                s.update({"model": model, "case": case, "variant": variant,
                          "finish": r["finish_reason"],
                          "latency_s": r["latency_s"],
                          "completion_tokens": r["completion_tokens"]})
                if r["finish_reason"] != "stop":
                    s["pass"] = False
                results.append(s)
                print(f"{model.split(':')[0]} | {case} | {variant} | "
                      f"finish={r['finish_reason']} verdict={s['verdict_ok']} "
                      f"cites={s['cites_ok']} invented={s['invented']} "
                      f"fmt={s['format_last_line']} PASS={s['pass']} "
                      f"({r['latency_s']}s, {r['completion_tokens']} tok)")
                (HERE / "ai-lab" / "reports" /
                 f"zeta-{stamp}-{model.split(':')[0]}-{case}-{variant}.txt"
                 ).write_text(f"MODEL: {model}\nCASE: {case}\nVARIANT: "
                              f"{variant}\nPROMPT:\n{prompt}\n\nRESPONSE:\n"
                              f"{r['text']}\n", encoding="utf-8")
    n = sum(1 for s in results if s["pass"])
    print(f"\n{n}/{len(results)} zeta cells passed")


if __name__ == "__main__":
    main()
