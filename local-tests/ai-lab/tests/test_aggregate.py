"""Offline tests for Arch B deterministic aggregation (no network).

Usage (from repo root): python local-tests/ai-lab/tests/test_aggregate.py
"""

import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

from evaluators import aggregate as agg

B = "DOCUMENTARY BLOCKER IDENTIFIED"
CLEAR = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"
INSUF = "INSUFFICIENT EVIDENCE"
PASS = 0


def check(name, cond, detail=""):
    global PASS
    assert cond, f"FAIL {name}: {detail}"
    PASS += 1
    print(f"  [ok] {name}")


# tb1 shape: stale decoy at wrong path -> CONFLICTING -> BLOCKER
TB1 = ("preset | render/preset.yaml | - | old/preset.yaml | "
       "# stale preset from 2023, superseded -- do not use | "
       "docs/restore-guide.md:6, old/preset.yaml:1 | STALE-MARKER-SEEN\n"
       "scene | scenes/shot01.blend | - | scenes/shot01.blend | "
       "BLEND synthetic placeholder | "
       "docs/restore-guide.md:4, scenes/shot01.blend:1 | OK")
# tb2 shape: same subject, two constraints -> CONFLICTING -> BLOCKER
TB2 = ("runtime | - | 3.0 or newer | config/runtime.txt | worker runtime 2.4.1 | "
       "docs/guide-v1.md:3, config/runtime.txt:1 | OK\n"
       "runtime | - | exactly 2.4.1 | config/runtime.txt | worker runtime 2.4.1 | "
       "docs/guide-v2.md:3, config/runtime.txt:1 | OK")
# tb3 shape: 3 satisfies >= 2 -> CLEAR
TB3 = ("webapp | app/main.py | - | app/main.py | print portal | "
       "docs/guide.md:3, app/main.py:1 | OK\n"
       "settings | config/app.txt | 2 or newer | config/app.txt | portal schema 3 | "
       "docs/guide.md:5, config/app.txt:1 | OK")
# tb4 shape: unreadable -> UNKNOWN -> INSUFFICIENT
TB4 = ("app | app/main.py | - | app/main.py | print offsite | "
       "docs/guide.md:3, app/main.py:1 | OK\n"
       "sheet | creds/sheet.txt | - | UNREADABLE | - | docs/guide.md:4 | "
       "access denied by manifest")
# tb5 shape: truncation -> UNKNOWN -> INSUFFICIENT
TB5 = ("calib | configs/calib.dat | 5 or newer | MISSING | - | "
       "docs/guide.md:5 | TRUNCATED-SOURCE\n"
       "TRUNC | docs/guide.md | page 2 requirements")
# tb6 shape: ALT relief -> CLEAR
TB6 = ("safety | - | - | MISSING | - | docs/guide.md:1 | OK\n"
       "snapshot | db/snapshot.sqlite | - | db/snapshot.sqlite | "
       "SQLite format 3 (synthetic snapshot) | "
       "docs/guide.md:4, db/snapshot.sqlite:1 | OK\n"
       "ALT | safety | db/pgdump.sql | db/snapshot.sqlite")

if __name__ == "__main__":
    check("tb1 blocker", agg.aggregate(TB1)["verdict"] == B)
    check("tb1 conflict label",
          agg.aggregate(TB1)["findings"][0]["label"] == "CONFLICTING")
    check("tb2 blocker", agg.aggregate(TB2)["verdict"] == B)
    check("tb3 clear", agg.aggregate(TB3)["verdict"] == CLEAR,
          str(agg.aggregate(TB3)))
    check("tb4 insuf", agg.aggregate(TB4)["verdict"] == INSUF)
    check("tb5 insuf", agg.aggregate(TB5)["verdict"] == INSUF,
          str(agg.aggregate(TB5)))
    check("tb6 clear", agg.aggregate(TB6)["verdict"] == CLEAR,
          str(agg.aggregate(TB6)))
    # adversarial micro-cases
    check("newer-major clear", agg.aggregate(
        "s | f | 2 or newer | f | version 10.1 | g:1, f:1 | OK")
        ["verdict"] == CLEAR)
    check("older-minor blocker", agg.aggregate(
        "s | f | 2.4 or newer | f | version 2.3.9 | g:1, f:1 | OK")
        ["verdict"] == B)
    check("exact-match clear", agg.aggregate(
        "s | f | exactly 2.4.1 | f | runtime 2.4.1 | g:1, f:1 | OK")
        ["verdict"] == CLEAR)
    check("exact-mismatch blocker", agg.aggregate(
        "s | f | exactly 2.4.1 | f | runtime 2.4.2 | g:1, f:1 | OK")
        ["verdict"] == B)
    check("tbd abstains", agg.aggregate(
        "s | f | protocol 3 | f | version: TBD | g:1, f:1 | OK")
        ["verdict"] == INSUF)
    check("empty fails closed", agg.aggregate(
        "ALT | s | a | b")["verdict"] == INSUF)
    check("blank fails closed", agg.aggregate(
        "\n  \n")["verdict"] == INSUF)
    print(f"{PASS} aggregation checks passed, ALL GREEN (offline)")
