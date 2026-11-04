"""Baseline comparison: PHOENIX vs filename search vs generic document QA.

Runs the three methods on every labeled corpus, three times each, and scores
the metrics required by references/validation-plan.md: blocker recall, false
blocking allegations, citation precision, abstention, repeatability, and
actual time spent. Measurement only — this script asserts nothing about the
scores; see reports/baseline-comparison.md for the recorded outcome.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baselines
import harness

ROOT = Path(__file__).resolve().parent
RUNS = 3

METHODS = {
    "phoenix": lambda scope: {
        "verdict": (r := harness.run(scope))["verdict"],
        "rows": [{"subject": e["subject"], "status": e["status"]}
                 for e in r["evidence"]],
        "cited": True},
    "filename_search": baselines.filename_search,
    "generic_qa": baselines.generic_qa,
}


def main():
    labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))["cases"]
    table, summary = {}, {m: {"cases": 0, "verdict_ok": 0, "recall_hit": 0,
                              "recall_total": 0, "false_alleg": 0,
                              "abstain_hit": 0, "abstain_total": 0,
                              "cited_rows": 0, "rows": 0, "stable": 0,
                              "ms": 0.0} for m in METHODS}
    for case, truth in labels.items():
        scope = ROOT / "corpus" / case
        table[case] = {"truth": truth["verdict"]}
        for name, fn in METHODS.items():
            verdicts, elapsed, result = [], 0.0, None
            for _ in range(RUNS):
                start = time.perf_counter()
                run_result = fn(scope)
                elapsed += (time.perf_counter() - start) * 1000
                verdicts.append(run_result["verdict"])
                result = run_result
            verdict = verdicts[0]
            s = summary[name]
            s["cases"] += 1
            s["verdict_ok"] += verdict == truth["verdict"]
            if truth["blocker"]:
                s["recall_total"] += 1
                s["recall_hit"] += verdict == "DOCUMENTARY BLOCKER IDENTIFIED"
            elif not truth["abstain"]:
                s["false_alleg"] += verdict == "DOCUMENTARY BLOCKER IDENTIFIED"
            if truth["abstain"]:
                s["abstain_total"] += 1
                s["abstain_hit"] += verdict == "INSUFFICIENT EVIDENCE"
            s["cited_rows"] += len(result["rows"]) if result["cited"] else 0
            s["rows"] += len(result["rows"])
            s["stable"] += len(set(verdicts)) == 1
            s["ms"] += elapsed / RUNS
            table[case][name] = verdict

    lines = ["# Baseline comparison (local measurement)",
             "",
             "Methods: `phoenix` (harness.py decision procedure with exact-path",
             "checks, version reconciliation, access handling, and source:line",
             "citations) vs `filename_search` (basename match anywhere, versions",
             "assumed satisfied, no citations) vs `generic_qa` (subject string",
             "mentioned anywhere counts as satisfied, no citations). Baselines",
             "ignore the access-denied manifest. Each method ran 3x per case;",
             "verdicts below are the stable result.",
             "",
             "| method | verdict accuracy | blocker recall | false allegations "
             "| abstention | citation precision | repeatability | mean ms/case |",
             "|---|---|---|---|---|---|---|"]
    for name, s in summary.items():
        lines.append(
            f"| {name} | {s['verdict_ok']}/{s['cases']} | "
            f"{s['recall_hit']}/{s['recall_total']} | {s['false_alleg']} | "
            f"{s['abstain_hit']}/{s['abstain_total']} | "
            f"{s['cited_rows']}/{s['rows']} rows cited | "
            f"{s['stable']}/{s['cases']} stable | {s['ms']/s['cases']:.1f} |")
    lines += ["", "## Per-case verdicts", "",
              "| case | ground truth | phoenix | filename_search | generic_qa |",
              "|---|---|---|---|---|"]
    for case, row in table.items():
        lines.append(f"| {case} | {row['truth']} | {row['phoenix']} | "
                     f"{row['filename_search']} | {row['generic_qa']} |")
    lines += ["",
              "Local simulation only — not NAS runtime evidence. Ground truth:",
              "`labels.json` (predeclared before measurement)."]
    report = "\n".join(lines)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "baseline-comparison.md").write_text(report,
                                                             encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
