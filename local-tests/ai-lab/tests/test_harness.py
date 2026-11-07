"""Offline unit tests for the ai-lab harness (no network, no spend).

Usage (from repo root): python local-tests/ai-lab/tests/test_harness.py
"""

import json
import sys
import tempfile
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

import budget as budget_mod
from evaluators import verdict as verdict_mod
from providers import vultr

PRICING = {"m": (1.0, 3.0)}  # $1/M in, $3/M out
PASS = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS
    assert cond, f"FAIL {name}: {detail}"
    PASS += 1
    print(f"  [ok] {name}")


def test_ledger():
    with tempfile.TemporaryDirectory() as tmp:
        led = budget_mod.Ledger(Path(tmp) / "l.jsonl", 0.01, 2, PRICING)
        check("empty totals", led.totals() == (0.0, 0))
        est = led.authorize("m", 300, 100)  # ~101 in-tok, 200 out-tok
        check("estimate positive", est > 0)
        led.record({"status": "ok", "cost_usd": 0.001})
        led.record({"status": "error", "cost_usd": 0.0})  # not counted
        spent, n = led.totals()
        check("error not counted", (spent, n) == (0.001, 1))
        led.record({"status": "ok", "cost_usd": 0.001})
        try:
            led.authorize("m", 300, 100)
            check("request cap trips", False)
        except budget_mod.BudgetExceeded:
            check("request cap trips", True)
        # cap survives restart (same file, new object, fresh counters)
        led2 = budget_mod.Ledger(Path(tmp) / "l.jsonl", 0.01, 5, PRICING)
        check("ledger persists", led2.totals() == (0.002, 2))
        try:
            led2.authorize("m", 300000, 100000)
            check("usd cap trips", False)
        except budget_mod.BudgetExceeded:
            check("usd cap trips", True)


def test_identity():
    check("exact", vultr.identities_match("a", "a"))
    check("normalize suffix", vultr.identities_match("a", "a-normalize"))
    check("mismatch rejected", not vultr.identities_match("a", "b"))
    check("empty rejected", not vultr.identities_match("a", ""))
    check("default-route rejected",
          not vultr.identities_match("glm-5.3", "glm-5.3-flash"))


def test_verdict():
    check("last wins", verdict_mod.parse_verdict(
        "VERDICT: <a|b>\nFINDINGS:\n- x\nVERDICT: INSUFFICIENT EVIDENCE\n")
        == "INSUFFICIENT EVIDENCE")
    check("none", verdict_mod.parse_verdict("nope") == "NO-VERDICT-LINE")
    check("offspec", verdict_mod.parse_verdict("VERDICT: MAYBE\n")
          .startswith("OFF-SPEC"))
    known = {"docs/guide.md": 5, "creds/sheet.txt": 1}
    r = verdict_mod.check_citations(
        "FINDINGS:\n- a (docs/guide.md:3)\n- b (nope/x.md:9)\n- c "
        "(docs/guide.md:99)\nVERDICT: INSUFFICIENT EVIDENCE\n", known)
    check("citations", r == {"resolved": ["docs/guide.md:3"],
                             "unresolved": ["nope/x.md:9",
                                            "docs/guide.md:99"]}, str(r))
    check("forbidden pct", verdict_mod.scan_forbidden(
        "FINDINGS:\n- a 95% ready\nVERDICT: INSUFFICIENT EVIDENCE\n") != [])
    check("forbidden restored", verdict_mod.scan_forbidden(
        "FINDINGS:\n- a was restored ok\nVERDICT: INSUFFICIENT EVIDENCE\n")
        != [])
    check("clean", verdict_mod.scan_forbidden(
        "FINDINGS:\n- a: FOUND — x (docs/guide.md:1)\n"
        "VERDICT: DOCUMENTARY BLOCKER IDENTIFIED\n") == [])


def test_no_secret_paths():
    src = (AI_LAB / "providers" / "vultr.py").read_text(encoding="utf-8")
    check("no key print", "print" not in src or "REDACTED" in src)
    check("scrub helper", "_scrub" in src and "[REDACTED]" in src)


if __name__ == "__main__":
    test_ledger()
    test_identity()
    test_verdict()
    test_no_secret_paths()
    print(f"{PASS} harness checks passed, ALL GREEN (offline)")
