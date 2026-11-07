"""Local acceptance tests for the PHOENIX workflow logic.

Each test runs harness.py against a synthetic corpus and asserts the exact
evidence labels and verdict required by references/validation-plan.md.
These are LOCAL simulations, not NAS runtime results.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baselines
import harness

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
CASES = ["core-a", "core-b", "edge", "core-c", "core-d", "edge-2",
         "edge-3", "scale"]

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
    ok &= check("plain-language blocker sentence present",
                "In plain terms:" in report and "do not assume" in report)

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
    lab = labels(result)
    ok &= check("verdict is INSUFFICIENT EVIDENCE",
                result["verdict"] == "INSUFFICIENT EVIDENCE",
                result["verdict"])
    ok &= check("denied file listed as inaccessible",
                "docs/secret-plan.md" in result["coverage"]["inaccessible"],
                str(result["coverage"]["inaccessible"]))
    ok &= check("denied content never leaked", "98452" not in report)
    ok &= check("truncated doc flagged",
                "docs/notes.md" in result["coverage"]["truncated"])
    ok &= check("truncated-source requirement is UNKNOWN",
                lab.get("app/tool.py") == "UNKNOWN", str(lab))
    ok &= check("injection ignored (no hostile wording, no escape)",
                all(s not in report for s in
                    ("..", "wipe", "entire filesystem", "exfiltrate", "curl",
                     "POST", "external server")))
    ok &= check("unicode filenames reviewed",
                any(ord(c) > 127 for p in result["coverage"]["reviewed"]
                    for c in p),
                str(result["coverage"]["reviewed"]))
    ok &= check("completion is PARTIAL (gaps present)",
                result.get("completion") == "PARTIAL",
                str(result.get("completion")))
    ok &= check("plain-language abstention sentence present",
                "In plain terms:" in report
                and "no conclusion is possible yet" in report)

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
    ok &= check("completion is COMPLETED (no gaps)",
                result.get("completion") == "COMPLETED",
                str(result.get("completion")))
    ok &= check("plain-language clear sentence present",
                "In plain terms:" in report
                and "still not a tested restore" in report)

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
                str({k: (len(v) if isinstance(v, list) else v)
                     for k, v in cov.items()}))
    ok &= check("missing file and unfounded version flagged",
                lab.get("config/missing.yaml") == "NOT FOUND IN SCOPE"
                and lab.get("worker") == "UNKNOWN", str(lab))

    print("edge-3 (denied reference, unsafe paths):")
    result, report = run_case("edge-3")
    lab = labels(result)
    cov = result["coverage"]
    ok &= check("verdict is INSUFFICIENT EVIDENCE",
                result["verdict"] == "INSUFFICIENT EVIDENCE",
                result["verdict"])
    ok &= check("denied reference is INACCESSIBLE",
                lab.get("docs/locked.md") == "INACCESSIBLE", str(lab))
    ok &= check("traversal subject rejected, never resolved",
                lab.get("../escape.txt") == "UNKNOWN"
                and "without resolving" in report
                and "escape.txt" not in str(cov["reviewed"]), str(lab))
    ok &= check("absolute subject rejected",
                lab.get("C:/abs.txt") == "UNKNOWN", str(lab))
    ok &= check("locked content never leaked", "77341" not in report)
    ok &= check("coverage exact (denied listed, manifest variant matched)",
                len(cov["reviewed"]) == 1 and len(cov["skipped"]) == 1
                and cov["inaccessible"] == ["docs/locked.md"],
                str({k: v for k, v in cov.items() if k != "symlinks_skipped"}))

    print("units (helpers):")
    ok &= check("version ordering sane",
                harness.compare("==", "1.2", "1.2")
                and harness.compare(">=", "3.1.0", "3.0")
                and harness.compare("<", "2.4.1", "3.0")
                and not harness.compare("==", "2.4.1", "2.4.1-beta"))
    nasty = [("==", "2.4.1-beta", "2.4.1"), ("<", "1.0", ""),
             ("==", "9" * 200, "9" * 200), (">=", "1..2", "1.0"),
             ("<", "", "0"), ("==", "v1.0 نهایی", "v1.0 نهایی")]
    try:
        nasty_ok = all(isinstance(harness.compare(op, a, b), bool)
                       for op, a, b in nasty)
    except Exception:
        nasty_ok = False
    ok &= check("version compare never raises", nasty_ok)
    ok &= check("long versions differing late compare unequal",
                not harness.compare("==", "1.0." + "9" * 100 + "a",
                                    "1.0." + "9" * 100 + "b")
                and harness.compare("==", "1.0." + "9" * 100 + "a",
                                    "1.0." + "9" * 100 + "a"))
    scope = ROOT / "corpus" / "core-a"
    ok &= check("safe_join accepts in-scope spellings",
                harness.safe_join(scope, "docs/checklist.md") is not None
                and harness.safe_join(scope, "docs//checklist.md") is not None)
    ok &= check("safe_join rejects escape/absolute/empty",
                harness.safe_join(scope, "a/../../x") is None
                and harness.safe_join(scope, "../x") is None
                and harness.safe_join(scope, "C:/x") is None
                and harness.safe_join(scope, "/etc/x") is None
                and harness.safe_join(scope, "") is None)
    ok &= check("norm_rel normalizes, rejects escape",
                harness.norm_rel("./docs//x.md") == "docs/x.md"
                and harness.norm_rel("a/../b") is None
                and harness.norm_rel("  ") is None)
    ok &= check("redact masks secrets, keeps facts",
                harness.redact("api-key=hunter2") == "api-key=[REDACTED]"
                and harness.redact("runtime 3.1.0") == "runtime 3.1.0"
                and harness.redact("password : s3cr3t") == "password=[REDACTED]"
                and harness.redact("access token=abc")
                == "access token=[REDACTED]"
                and harness.redact("connection string=mongodb://u:p@h/db")
                == "connection string=[REDACTED]"
                and harness.redact("leaked ghp_0123456789abcdefZZ")
                == "leaked [REDACTED-TOKEN]"
                and harness.redact("key sk-abcdefgh12345678 here")
                == "key [REDACTED-TOKEN] here")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "doc.md").write_text("REQUIRES: app/main.py\n", encoding="utf-8")
        (t / "access-denied.txt").write_bytes(b"\xff\xfe\x00binary")
        try:
            res = harness.run(t)
            binary_ok = res["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED"
        except Exception:
            binary_ok = False
    ok &= check("binary manifest cannot crash run", binary_ok)
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "nope.md"
        ok &= check("OS errors map to None, never raise",
                    harness._safe_probe(missing) is None
                    and harness._safe_read(missing) is None)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        deep = t
        for i in range(15):
            deep = deep / f"level{i}"
            deep.mkdir()
        (deep / "buried.md").write_text("REQUIRES: app/main.py\n",
                                        encoding="utf-8")
        (t / "top.md").write_text("REQUIRES: app/main.py\n", encoding="utf-8")
        (t / "app").mkdir()
        (t / "app" / "main.py").write_text("x\n", encoding="utf-8")
        res = harness.run(t)
        ok &= check("depth cap bounds deep trees",
                    res["coverage"]["depth_capped"] >= 1
                    and res["completion"] == "PARTIAL"
                    and res["verdict"] == "INSUFFICIENT EVIDENCE",
                    str(res["coverage"]["depth_capped"]))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "big.md").write_text("# Big\n\n" + "padding line\n" * 100000
                                  + "REQUIRES: app/main.py\n", encoding="utf-8")
        (t / "app").mkdir()
        (t / "app" / "main.py").write_text("x\n", encoding="utf-8")
        start = time.perf_counter()
        res = harness.run(t)
        big_ms = (time.perf_counter() - start) * 1000
        print(f"  [info] 1.3 MB doc run: {big_ms:.0f} ms")
        ok &= check("large document processed correctly",
                    res["verdict"] == "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"
                    and res["coverage"]["reviewed"] == ["big.md"],
                    res["verdict"])
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "guide.md").write_text("REQUIRES: worker >= 2.0\n",
                                    encoding="utf-8")
        out = baselines.retrieval_plus(t)
        ok &= check("retrieval_plus cites sources, abstains when unfounded",
                    out["verdict"] == "INSUFFICIENT EVIDENCE"
                    and out["cited"] is True
                    and out["rows"]
                    and out["rows"][0].get("source") == "guide.md:1",
                    str(out))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "guide.md").write_text("REQUIRES: runtime >= 3.0\n",
                                    encoding="utf-8")
        (t / "old.yaml").write_text("PROVIDES: runtime 2.4.1\n",
                                    encoding="utf-8")
        (t / "new.yaml").write_text("PROVIDES: runtime 3.1.0\n",
                                    encoding="utf-8")
        res = harness.run(t)
        alt = labels(res)
        ok &= check("alternative provisions resolve when one satisfies",
                    alt.get("runtime") == "FOUND"
                    and res["verdict"] == "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
                    str(alt))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "doc.md").write_text("REQUIRES: link.md\n", encoding="utf-8")
        (t / "real.md").write_text("hello\n", encoding="utf-8")
        try:
            os.symlink(t / "real.md", t / "link.md")
            linked = True
        except (OSError, NotImplementedError):
            linked = False
        if linked:
            res = harness.run(t)
            assert res["coverage"]["symlinks_skipped"] == ["link.md"], \
                "symlink followed!"
            assert sorted(res["coverage"]["reviewed"]) == ["doc.md",
                                                           "real.md"], \
                "target misread!"
            nover = harness.run(t, mode="no_verify")
            assert nover["evidence"][0]["status"] == "NOT FOUND IN SCOPE", \
                "symlink basename leaked into no_verify match!"
            print("  [PASS] symlinked file skipped (conditional, uncounted)")
        else:
            print("  [SKIP] symlink creation needs privileges")

    print("closure (recheck + delta, scenarios A/B/C):")
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp) / "case-a"
        shutil.copytree(ROOT / "corpus" / "core-a", t)
        before = harness.run(t)
        (t / "config").mkdir(parents=True, exist_ok=True)
        (t / "config" / "prod-config.yaml").write_text(
            "# supplied by operator\n", encoding="utf-8")
        after = harness.run(t, prior=before)
        delta = after["delta"]
        trans = {tr["subject"]: tr["state"] for tr in delta["transitions"]}
        ok &= check("A: verdict BLOCKER -> CLEAR",
                    before["verdict"] == "DOCUMENTARY BLOCKER IDENTIFIED"
                    and after["verdict"] == "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
                    f"{before['verdict']} -> {after['verdict']}")
        ok &= check("A: missing asset RESOLVED with new evidence",
                    trans.get("config/prod-config.yaml") == "RESOLVED"
                    and "verified present" in str(delta["transitions"]),
                    str(trans))
        ok &= check("A: recheck report carries section 9, first run does not",
                    "## 9. Recovery Delta" in after["report"]
                    and "## 9. Recovery Delta" not in before["report"])
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp) / "case-b"
        shutil.copytree(ROOT / "corpus" / "core-b", t)
        before = harness.run(t)
        (t / "config" / "runtime.yaml").write_text(
            "# bumped by operator\nPROVIDES: runtime 3.0\n", encoding="utf-8")
        after = harness.run(t, prior=before)
        trans = {tr["subject"]: tr["state"] for tr in after["delta"]["transitions"]}
        ok &= check("B: conflict RESOLVED after version fix",
                    trans.get("runtime") == "RESOLVED"
                    and after["verdict"] == "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
                    str(trans))
        sec9 = after["report"].split("## 9. Recovery Delta")[1]
        ok &= check("B: delta never claims restoration",
                    "not a tested restoration" in sec9
                    and all(s not in sec9.lower() for s in
                            ("restored", "recovery complete", "system restored")),
                    sec9[:200])
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "guide.md").write_text(
            "REQUIRES: tool.py\nREQUIRES: license >= 2.0\n", encoding="utf-8")
        (t / "tool.py").write_text("x\n", encoding="utf-8")
        before = harness.run(t)
        (t / "readme.txt").write_text("unrelated note\n", encoding="utf-8")
        after = harness.run(t, prior=before)
        trans = {tr["subject"]: tr["state"] for tr in after["delta"]["transitions"]}
        ok &= check("C: unverified stays uncertain after irrelevant change",
                    before["verdict"] == "INSUFFICIENT EVIDENCE"
                    and after["verdict"] == "INSUFFICIENT EVIDENCE"
                    and trans.get("license") == "STILL UNCERTAIN"
                    and trans.get("tool.py") == "UNCHANGED",
                    str(trans))
        ok &= check("C: nothing falsely RESOLVED",
                    all(tr["state"] != "RESOLVED"
                        for tr in after["delta"]["transitions"]))
    sec7 = (REPORTS / "core-d.md").read_text(encoding="utf-8")
    sec7 = sec7.split("## 7. Next steps")[1].split("## 8. Verdict")[0]
    rec_lines = [ln for ln in sec7.splitlines() if ln.startswith("- ")]
    ok &= check("recommendations prioritize blockers with evidence",
                bool(rec_lines) and rec_lines[0].startswith("- P1:")
                and "deployment-guide.md" in sec7,
                str(rec_lines[:2]))
    ok &= check("recommendations never claim restore-like action",
                bool(rec_lines) and all(not harness.violates_restore_ban(ln)
                                        for ln in rec_lines),
                str(rec_lines))
    sec5 = (REPORTS / "core-b.md").read_text(encoding="utf-8")
    sec5 = sec5.split("## 5. Priority blockers")[1].split("## 6. ")[0]
    ok &= check("blockers explain impact",
                "impact:" in sec5 and "CONFLICTING" in sec5)
    ok &= check("first-run reports carry no delta section",
                "## 9. Recovery Delta" not in (REPORTS / "core-a.md").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "g.md").write_text("REQUIRES: a.txt\n", encoding="utf-8")
        p1 = t / "before.json"
        r1 = subprocess.run([sys.executable, str(ROOT / "harness.py"), str(t), str(p1)],
                            capture_output=True, text=True)
        (t / "a.txt").write_text("x\n", encoding="utf-8")
        p2 = t / "after.json"
        r2 = subprocess.run([sys.executable, str(ROOT / "harness.py"), str(t), str(p2), str(p1)],
                            capture_output=True, text=True)
        ok &= check("CLI accepts prior report, emits delta",
                    r1.returncode == 0 and r2.returncode == 0
                    and "## 9. Recovery Delta" in r2.stdout
                    and "RESOLVED" in r2.stdout)

    print("skill/report vocabulary guard:")
    skill = (ROOT.parent / "SKILL.md").read_text(encoding="utf-8")
    sentence = skill.split("exactly these sections:")[1].split(".")[0]
    sample = (REPORTS / "core-a.md").read_text(encoding="utf-8")
    headings = [ln[6:].split(":")[0] for ln in sample.splitlines()
                if ln.startswith("## ")]
    ok &= check("every report heading noun appears in SKILL.md",
                all(h.lower() in sentence.lower() for h in headings),
                str(headings))

    print("report contract (8 sections):")
    for case in CASES:
        text = (REPORTS / f"{case}.md").read_text(encoding="utf-8")
        want = ["## 1. Scenario", "## 2. Coverage", "## 3. Requirements",
                "## 4. Evidence table", "## 5. Priority blockers",
                "## 6. Contradictions",
                "## 7. Next steps", "## 8. Verdict: "]
        ok &= check(f"{case} has all 8 sections",
                    all(h in text for h in want))

    print(f"\n{CHECKS_PASSED} checks passed, "
          f"{'ALL GREEN' if ok else 'FAILURES PRESENT'} "
          f"(local simulation only — not NAS runtime evidence).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
