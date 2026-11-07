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
        "s | f | 2 or newer | f | version 10.1 | g.md:1, f.txt:1 | OK")
        ["verdict"] == CLEAR)
    check("older-minor blocker", agg.aggregate(
        "s | f | 2.4 or newer | f | version 2.3.9 | g.md:1, f.txt:1 | OK")
        ["verdict"] == B)
    check("exact-match clear", agg.aggregate(
        "s | f | exactly 2.4.1 | f | runtime 2.4.1 | g.md:1, f.txt:1 | OK")
        ["verdict"] == CLEAR)
    check("exact-mismatch blocker", agg.aggregate(
        "s | f | exactly 2.4.1 | f | runtime 2.4.2 | g.md:1, f.txt:1 | OK")
        ["verdict"] == B)
    check("tbd abstains", agg.aggregate(
        "s | f | protocol 3 | f | version: TBD | g.md:1, f.txt:1 | OK")
        ["verdict"] == INSUF)
    check("empty fails closed", agg.aggregate(
        "ALT | s | a | b")["verdict"] == INSUF)
    check("blank fails closed", agg.aggregate(
        "\n  \n")["verdict"] == INSUF)
    check("same-name-diff-file no conflict", agg.aggregate(
        "s | a/f | - | a/f | x | g.md:1 | OK\n"
        "s | b/f | 3 | b/f | version 3 | g.md:2 | OK")["verdict"] == CLEAR)
    check("same-file-diff-constraint conflicts", agg.aggregate(
        "s | - | 3 or newer | c/f | v 2 | g.md:1 | OK\n"
        "s | - | exactly 2 | c/f | v 2 | g.md:2 | OK")["verdict"] == B)
    check("observed-values disagree", agg.aggregate(
        "port | - | - | a/f | port 9090 | g.md:1 | OK\n"
        "port | - | - | b/f | port 8080 | g.md:2 | OK")["verdict"] == B)
    check("observed-values agree", agg.aggregate(
        "port | - | - | a/f | port 9090 | g.md:1 | OK\n"
        "port | - | - | b/f | port 9090 (confirmed) | g.md:2 | OK")
        ["verdict"] == CLEAR)
    check("non-numeric restatement ignored", agg.aggregate(
        "port | - | - | a/f | port 9090 | g.md:1 | OK\n"
        "port | - | - | g/f | listens on the documented port | g.md:2 | OK")
        ["verdict"] == CLEAR)
    check("wrapped row joined", agg.aggregate(
        "preset | r/p.yaml | - | o/p.yaml | # stale preset from 2023\n"
        "exposure: old | docs/g.md:6, o/p.yaml:1 | STALE-MARKER-SEEN")
        ["verdict"] == B)
    check("chatter line skipped", agg.aggregate(
        "Now I will format: SUBJECT | A | B | C | D | E | F\n"
        "s | f | - | f | x | g.md:1 | OK")["verdict"] == CLEAR)
    check("path-echo constraint ignored", agg.aggregate(
        "s | a/f | a/f | a/f | x | g.md:1 | OK")["verdict"] == CLEAR)
    check("tab-separated rows", agg.aggregate(
        "s\tf.txt\t2 or newer\tf.txt\tversion 3\tg.md:1\tOK")
        ["verdict"] == CLEAR)
    check("mixed tabs and pipes", agg.aggregate(
        "s\tf.txt\t2 or newer\tf.txt\tversion 3\tg.md:1\tOK\n"
        "t | g.txt | - | g.txt | x | h.md:2 | OK")["verdict"] == CLEAR)
    check("markdown chatter skipped", agg.aggregate(
        "**Line 1:** `s | f | - | f | x | g.md:1 | OK`\n"
        "s | f | - | f | x | g.md:1 | OK")["verdict"] == CLEAR)
    check("prose never glues rows", agg.aggregate(
        "Some thinking without separators\n"
        "s | f | - | f | x | g.md:1 | OK\n"
        "More thinking here")["verdict"] == CLEAR)
    check("alternatively-prose dropped", agg.aggregate(
        "Alternatively, I could output two lines\n"
        "s | f | - | f | x | g.md:1 | OK")["verdict"] == CLEAR)
    check("bare-version equal found", agg.aggregate(
        "s | f | format 6 | f | routes format 6 | g.md:1 | OK")
        ["verdict"] == CLEAR)
    check("bare-version differ abstains", agg.aggregate(
        "s | f | format 6 | f | routes format 5 | g.md:1 | OK")
        ["verdict"] == INSUF)
    check("alt matches by option path", agg.aggregate(
        "cron | a/cron | - | MISSING | - | g.md:1 | OK\n"
        "timer | a/timer | - | a/timer | x | g.md:2 | OK\n"
        "ALT | job group | a/cron | a/timer")["verdict"] == CLEAR)
    print(f"{PASS} aggregation checks passed, ALL GREEN (offline)")
