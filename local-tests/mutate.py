"""Mutation testing for the PHOENIX local harness and baselines.

Applies concrete mutations to a scratch copy of local-tests/, runs the
full acceptance suite against each mutant, and reports the kill rate.
A surviving mutant is a real coverage gap, not a passing grade.
Exit 0 only when every mutant is killed.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Each mutant: (name, [(relative path, exact anchor, replacement), ...]).
# Single-edit mutants carry a one-element list; the double mutant proves
# the suite still fails when two defects land at once.
MUTANTS = [
    ("verdict-blocker-swapped", [("harness.py",
      '    if statuses & {NOT_FOUND, CONFLICTING}:\n'
      '        verdict = "DOCUMENTARY BLOCKER IDENTIFIED"',
      '    if statuses & {NOT_FOUND, CONFLICTING}:\n'
      '        verdict = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"')]),
    ("denied-check-removed", [("harness.py",
      "            if norm is not None and norm in denied:",
      "            if False:  # MUTANT")]),
    ("version-compare-flipped", [("harness.py",
      '">": a > w, "<": a < w}[op]',
      '">": a < w, "<": a > w}[op]')]),
    ("truncation-rule-removed", [("harness.py",
      '        if req["truncated_source"]:',
      "        if False:  # MUTANT")]),
    ("containment-neutered", [("harness.py",
      "        candidate.relative_to(scope)",
      "        candidate.relative_to(candidate.parent)  # MUTANT")]),
    ("redact-neutered", [("harness.py",
      '    return TOKEN_RE.sub("[REDACTED-TOKEN]", masked)',
      "    return text  # MUTANT")]),
    ("existence-oracle-true", [("harness.py",
      "            elif target.exists():",
      "            elif True:  # MUTANT")]),
    ("abstention-verdict-swapped", [("harness.py",
      '    elif (statuses & {INACCESSIBLE, UNKNOWN} or inaccessible_files\n'
      '          or discovery_errors or depth_capped):\n'
      '        verdict = "INSUFFICIENT EVIDENCE"',
      '    elif (statuses & {INACCESSIBLE, UNKNOWN} or inaccessible_files\n'
      '          or discovery_errors or depth_capped):\n'
      '        verdict = "DOCUMENTARY BLOCKER IDENTIFIED"')]),
    ("truncation-hash-removed", [("harness.py",
      '    key.append((2, len(version),\n'
      '                hashlib.sha256(version.encode("utf-8",\n'
      '                                              errors="replace")).hexdigest()))',
      "    pass  # MUTANT: hash tail removed")]),
    ("redact-token-neutered", [("harness.py",
      '    return TOKEN_RE.sub("[REDACTED-TOKEN]", masked)',
      "    return masked  # MUTANT")]),
    ("completion-always-completed", [("harness.py",
      '        completion = "PARTIAL"',
      '        completion = "COMPLETED"  # MUTANT')]),
    ("depth-cap-removed", [("harness.py",
      "        if len(path.relative_to(scope).parts) > MAX_DEPTH:",
      "        if False:  # MUTANT")]),
    ("retrieval-abstention-removed", [("baselines.py",
      'ABSTAIN = "INSUFFICIENT EVIDENCE"',
      "ABSTAIN = CLEAR  # MUTANT")]),
    ("double-verdict-plus-redact", [
      ("harness.py",
       '    if statuses & {NOT_FOUND, CONFLICTING}:\n'
       '        verdict = "DOCUMENTARY BLOCKER IDENTIFIED"',
       '    if statuses & {NOT_FOUND, CONFLICTING}:\n'
       '        verdict = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"'),
      ("harness.py",
       '    return TOKEN_RE.sub("[REDACTED-TOKEN]", masked)',
       "    return text  # MUTANT")]),
    ("delta-stale-reuse", [("harness.py",
      '        new_map = {e["subject"]: e["status"] for e in evidence}',
      '        new_map = {e["subject"]: e["status"] for e in prior.get("evidence", [])}  # MUTANT')]),
    ("delta-inversion", [("harness.py",
      '            state = "RESOLVED"',
      '            state = "STILL BLOCKED"  # MUTANT')]),
]


def main():
    kills, survivors = [], []
    for name, edits in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "local-tests"
            shutil.copytree(ROOT, work,
                            ignore=shutil.ignore_patterns(
                                "wave1", "reports", "__pycache__"))
            for rel, find, replace in edits:
                target = work / rel
                text = target.read_text(encoding="utf-8")
                assert text.count(find) == 1, f"mutant anchor drifted: {name}"
                target.write_text(text.replace(find, replace), encoding="utf-8")
            proc = subprocess.run([sys.executable, "run-tests.py"], cwd=work,
                                  capture_output=True, text=True)
            failed = [line for line in proc.stdout.splitlines()
                      if "[FAIL]" in line]
            if proc.returncode != 0 and failed:
                kills.append((name, failed[0].strip()))
                print(f"  [KILLED] {name} <- {failed[0].strip()}")
            else:
                survivors.append(name)
                print(f"  [SURVIVED] {name} <- COVERAGE GAP")
    print(f"\nmutation score: {len(kills)}/{len(MUTANTS)} killed")
    return 0 if not survivors else 1


if __name__ == "__main__":
    sys.exit(main())
