"""Baseline comparison: PHOENIX vs ablations vs naive alternatives.

Runs six methods on every labeled corpus, three times each: full PHOENIX,
two PHOENIX ablations (no reconciliation, no verification), a
retrieval-plus-analysis approach, filename search, and generic document QA.
Scores verdict accuracy, blocker precision/recall, false clears, false
blockers, abstention, citation precision, version-conflict detection,
repeatability, and time. Measurement only — asserts nothing about scores;
see reports/baseline-comparison.md for the recorded outcome.
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

def _phoenix_mode(mode):
    def run_mode(scope):
        result = harness.run(scope, mode=mode)
        return {"verdict": result["verdict"],
                "rows": [{"subject": e["subject"], "status": e["status"]}
                         for e in result["evidence"]],
                "cited": True}
    return run_mode


METHODS = {
    "phoenix": _phoenix_mode("full"),
    "phoenix_no_reconcile": _phoenix_mode("no_reconcile"),
    "phoenix_no_verify": _phoenix_mode("no_verify"),
    "retrieval_plus": baselines.retrieval_plus,
    "filename_search": baselines.filename_search,
    "generic_qa": baselines.generic_qa,
}

CONFLICT_CASES = ("core-b", "core-d", "edge-2")


def main():
    labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))["cases"]
    table, summary = {}, {m: {"cases": 0, "verdict_ok": 0, "recall_hit": 0,
                              "recall_total": 0, "false_alleg": 0,
                              "abstain_hit": 0, "abstain_total": 0,
                              "cited_rows": 0, "rows": 0, "stable": 0,
                              "ms": 0.0, "tp": 0, "fp": 0,
                              "false_clear": 0, "conflict_hit": 0,
                              "conflict_total": 0} for m in METHODS}
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
            called_blocker = verdict == "DOCUMENTARY BLOCKER IDENTIFIED"
            if truth["blocker"]:
                s["recall_total"] += 1
                s["recall_hit"] += called_blocker
                s["tp"] += called_blocker
                s["false_clear"] += (verdict == "NO DOCUMENTARY BLOCKER "
                                                 "FOUND IN REVIEWED SOURCES")
            else:
                s["fp"] += called_blocker
                if not truth["abstain"]:
                    s["false_alleg"] += called_blocker
            if truth["abstain"]:
                s["abstain_total"] += 1
                s["abstain_hit"] += verdict == "INSUFFICIENT EVIDENCE"
            if case in CONFLICT_CASES:
                s["conflict_total"] += 1
                s["conflict_hit"] += called_blocker
            s["cited_rows"] += len(result["rows"]) if result["cited"] else 0
            s["rows"] += len(result["rows"])
            s["stable"] += len(set(verdicts)) == 1
            s["ms"] += elapsed / RUNS
            table[case][name] = verdict

    lines = ["# Baseline comparison (local measurement)",
             "",
             "Methods: `phoenix` (full decision procedure: exact-path checks,",
             "version reconciliation, access handling, source:line citations);",
             "`phoenix_no_reconcile` (contradictions degrade to UNKNOWN);",
             "`phoenix_no_verify` (basename matching instead of exact paths);",
             "`retrieval_plus` (exact paths plus version compare, binary",
             "BLOCKER/CLEAR verdict, no abstention, no citations);",
             "`filename_search` (basename match anywhere, versions assumed",
             "satisfied, no citations); `generic_qa` (subject string mentioned",
             "anywhere counts as satisfied, no citations). Non-PHOENIX methods",
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
    lines += ["", "## Extended metrics (absolute counts)", "",
              "| method | blocker precision tp/(tp+fp) | false clears | "
              "false blockers | version-conflict detection |",
              "|---|---|---|---|---|"]
    for name, s in summary.items():
        lines.append(f"| {name} | {s['tp']}/({s['tp']}+{s['fp']}) | "
                     f"{s['false_clear']} | {s['fp']} | "
                     f"{s['conflict_hit']}/{s['conflict_total']} |")
    lines += ["", "## Per-case verdicts", "",
              "| case | ground truth | phoenix | no_reconcile | no_verify |",
              "|---|---|---|---|---|"]
    for case, row in table.items():
        lines.append(f"| {case} | {row['truth']} | {row['phoenix']} | "
                     f"{row['phoenix_no_reconcile']} | "
                     f"{row['phoenix_no_verify']} |")
    lines += ["", "## Per-case verdicts, naive methods", "",
              "| case | ground truth | retrieval_plus | filename_search | "
              "generic_qa |",
              "|---|---|---|---|---|"]
    for case, row in table.items():
        lines.append(f"| {case} | {row['truth']} | {row['retrieval_plus']} | "
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
