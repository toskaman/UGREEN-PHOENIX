"""Cross-document consistency guard (v9 D1 regression test).

Runs the offline suites live, counts mutants statically, regenerates the
baseline report, and asserts every public number in README.md,
local-tests/devpost-kit.md, A SOUMETTRE/build_pdf.py, and
local-tests/native-transfer-report.md matches the measured value.
A stale doc claim (e.g. v8's 86/86 vs 91/91) fails here, not in review.
Exit 0 only when all numbers agree. Run from the repo root:
python local-tests/check_consistency.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()
HERE = ROOT / "local-tests"
FAIL = []


def fail(msg):
    FAIL.append(msg)
    print(f"  [FAIL] {msg}")


def run_suite(path, want):
    """Run a suite, require exit 0 + ALL GREEN, return passed count."""
    proc = subprocess.run([sys.executable, str(path)], capture_output=True,
                          text=True, cwd=ROOT)
    tail = "\n".join(proc.stdout.strip().splitlines()[-3:])
    m = re.search(r"(\d+)\D+checks passed", proc.stdout)
    n = int(m.group(1)) if m else None
    green = "ALL GREEN" in proc.stdout and proc.returncode == 0
    print(f"  suite {Path(path).name}: n={n} green={green} want={want}")
    if not green or n != want:
        fail(f"{path}: ran n={n} green={green}, want={want}\n{tail}")
    return n


def expect(doc, needle, why):
    text = (ROOT / doc).read_text(encoding="utf-8")
    ok = needle in text
    print(f"  {'[ok]' if ok else '[MISS]'} {doc} :: {needle!r} ({why})")
    if not ok:
        fail(f"{doc} missing {needle!r} ({why})")


def main():
    print("live suites:")
    n_accept = run_suite(HERE / "run-tests.py", 92)
    n_agg = run_suite(HERE / "ai-lab/tests/test_aggregate.py", 147)
    n_pg = run_suite(HERE / "test_proofgraph.py", 39)
    n_hn = run_suite(HERE / "ai-lab/tests/test_harness.py", 31)
    n_bg = run_suite(HERE / "ai-lab/tests/test_budget.py", 35)
    n_sc = run_suite(HERE / "test_skill_contract.py", 20)
    n_adv = run_suite(HERE / "test_adversarial.py", 15)

    sys.path.insert(0, str(HERE))
    import mutate
    n_mut = len(mutate.MUTANTS)
    print(f"  mutants defined: {n_mut} (static; full kill run is separate)")
    if n_mut != 17:
        fail(f"mutate.py defines {n_mut} mutants, docs claim 17")

    print("baseline regeneration:")
    proc = subprocess.run([sys.executable, str(HERE / "run-baseline.py")],
                          capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        fail(f"run-baseline.py exit {proc.returncode}\n"
             f"{proc.stderr[:500]}")
    rep = (HERE / "reports/baseline-comparison.md").read_text(
        encoding="utf-8")
    cells = {}
    for m in re.finditer(
            r"\| (phoenix|retrieval_plus|filename_search|generic_qa) \| "
            r"(\d+/\d+) \| (\d+/\d+) \| \d+ \| (\d+/\d+) \| "
            r"(\d+/\d+) rows cited", rep):
        cells[m.group(1)] = m.groups()[1:]
    print(f"  baseline cells: {cells}")
    want_cells = {
        "phoenix": ("8/8", "5/5", "2/2", "22/22"),
        "retrieval_plus": ("6/8", "5/5", "0/2", "22/22"),
        "filename_search": ("3/8", "2/5", "0/2", "0/22"),
        "generic_qa": ("1/8", "0/5", "0/2", "0/22"),
    }
    if cells != want_cells:
        fail(f"baseline report cells {cells} != {want_cells}")

    print("doc claims:")
    counts = {92: n_accept, 147: n_agg, 39: n_pg, 31: n_hn, 35: n_bg,
              20: n_sc, 15: n_adv, 17: n_mut}
    for n, live in counts.items():
        if live != n:
            continue  # already failed above; skip doc echo
        expect("README.md", f"{n}/{n}", "test table")
    expect("local-tests/devpost-kit.md", "92/92", "workflow logic")
    expect("local-tests/devpost-kit.md", "17/17", "mutation kills")
    expect("local-tests/devpost-kit.md", "8/8", "phoenix verdicts")
    expect("local-tests/devpost-kit.md", "22/22", "citations")
    expect("A SOUMETTRE/build_pdf.py", "92/92", "proposal evidence")
    expect("A SOUMETTRE/build_pdf.py", "17/17", "proposal evidence")
    expect("local-tests/native-transfer-report.md", "39/39", "proof graph")
    expect("README.md", "PHOENIX 8/8", "baseline row")
    expect("README.md", "retrieval-plus 6/8", "baseline row")

    if FAIL:
        print(f"\n{len(FAIL)} CONSISTENCY FAILURES")
        sys.exit(1)
    print("\nconsistency OK: all public numbers match live measurements")


if __name__ == "__main__":
    main()
