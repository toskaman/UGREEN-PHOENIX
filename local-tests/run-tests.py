"""Local acceptance tests for the PHOENIX workflow logic.

Each test runs harness.py against a synthetic corpus and asserts the exact
evidence labels and verdict required by references/validation-plan.md.
These are LOCAL simulations, not NAS runtime results.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
CASES = ["core-a", "core-b", "edge"]

CHECKS_PASSED = 0


def check(name, condition, detail=""):
    global CHECKS_PASSED
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if condition:
        CHECKS_PASSED += 1
    return condition


def run_case(case):
    out_json = REPORTS / f"{case}.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "harness.py"),
         str(ROOT / "corpus" / case), str(out_json)],
        capture_output=True, text=True)
    report = proc.stdout
    (REPORTS / f"{case}.md").write_text(report, encoding="utf-8")
    assert proc.returncode == 0, f"harness crashed on {case}: {proc.stderr}"
    import json
    return json.loads(out_json.read_text(encoding="utf-8")), report


def labels(result):
    return {e["subject"]: e["status"] for e in result["evidence"]}


def status_list(result):
    return [(e["subject"], e["status"]) for e in result["evidence"]]


def main():
    REPORTS.mkdir(exist_ok=True)
    ok = True

    print("core-a (required artifact absent):")
    result, report = run_case("core-a")
    lab = labels(result)
    ok &= check("verdict is DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"])
    ok &= check("present file is FOUND",
                lab.get("app/main.py") == "FOUND", str(lab))
    ok &= check("absent asset is NOT FOUND IN SCOPE",
                lab.get("config/prod-config.yaml") == "NOT FOUND IN SCOPE",
                str(lab))
    ok &= check("no global-absence claim",
                all(s not in report for s in
                    ("does not exist anywhere", "impossible to recover",
                     "backup is defective")))
    ok &= check("stale decoy seen but correctly rejected",
                "old-backup/prod-config.yaml" in result["coverage"]["reviewed"]
                and lab.get("config/prod-config.yaml") == "NOT FOUND IN SCOPE")

    print("core-b (present but incompatible version):")
    result, report = run_case("core-b")
    lab = labels(result)
    ok &= check("verdict is DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"])
    ok &= check("contradicted version is CONFLICTING",
                lab.get("runtime") == "CONFLICTING", str(lab))
    ok &= check("both sources cited",
                "deployment-guide.md" in report and "runtime.yaml" in report)
    ok &= check("no restored status claimed", "restored" not in report.lower()
                or "not a verified restore" in report.lower())

    print("edge (denied access, truncated doc, embedded injection):")
    result, report = run_case("edge")
    ok &= check("verdict is INSUFFICIENT EVIDENCE",
                result["verdict"] == "INSUFFICIENT EVIDENCE",
                result["verdict"])
    ok &= check("denied file listed as inaccessible",
                "docs/secret-plan.md" in result["coverage"]["inaccessible"],
                str(result["coverage"]["inaccessible"]))
    ok &= check("denied content never leaked", "98452" not in report)
    ok &= check("truncated doc flagged",
                "docs/notes.md" in result["coverage"]["truncated"])
    ok &= check("injection ignored (no hostile wording, no escape)",
                all(s not in report for s in ("..", "wipe", "entire filesystem")))

    print("core-c (healthy project, no blocker):")
    result, report = run_case("core-c")
    lab = labels(result)
    ok &= check("verdict is NO DOCUMENTARY BLOCKER FOUND",
                result["verdict"] == "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
                result["verdict"])
    ok &= check("every requirement FOUND",
                all(lab.get(s) == "FOUND"
                    for s in ("app/main.py", "config/app.yaml", "runtime")),
                str(lab))

    print("core-d (mixed evidence):")
    result, report = run_case("core-d")
    lab = labels(result)
    ok &= check("verdict is DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"])
    ok &= check("mixed labels exact",
                lab.get("app/main.py") == "FOUND"
                and lab.get("config/missing.yaml") == "NOT FOUND IN SCOPE"
                and lab.get("runtime") == "CONFLICTING", str(lab))

    print("edge-2 (guides disagree):")
    result, report = run_case("edge-2")
    statuses = status_list(result)
    ok &= check("verdict is DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"])
    ok &= check("disagreement surfaces as CONFLICTING",
                ("runtime", "CONFLICTING") in statuses, str(statuses))
    ok &= check("both guides cited",
                "guide-v1.md" in report and "guide-v2.md" in report)

    print("scale (40 filler docs):")
    result, report = run_case("scale")
    lab = labels(result)
    cov = result["coverage"]
    ok &= check("verdict is DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED",
                result["verdict"])
    ok &= check("coverage counts exact",
                len(cov["reviewed"]) == 42 and len(cov["skipped"]) == 1,
                str({k: len(v) for k, v in cov.items()}))
    ok &= check("missing file and unfounded version flagged",
                lab.get("config/missing.yaml") == "NOT FOUND IN SCOPE"
                and lab.get("worker") == "UNKNOWN", str(lab))

    print(f"\n{CHECKS_PASSED} checks passed, "
          f"{'ALL GREEN' if ok else 'FAILURES PRESENT'} "
          f"(local simulation only — not NAS runtime evidence).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
