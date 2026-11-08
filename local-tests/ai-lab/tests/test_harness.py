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
from evaluators import redact as redact_mod
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
        check("empty totals", led.totals() == (0.0, 0.0, 0, 0))
        rid, est = led.reserve("r1", "m", "tb1", "t", 300, 100)
        check("estimate positive", est > 0 and rid == "r1")
        spent, held, n, corrupt = led.totals()
        check("reservation held", held == est and spent == 0.0 and n == 1)
        led.fail_no_charge("r1", note="t")
        spent, held, n, corrupt = led.totals()
        check("no-charge frees hold, keeps slot",
              held == 0.0 and spent == 0.0 and n == 1)
        led.reserve("r2", "m", "tb1", "t", 300, 100)
        led.complete("r2", 0.001, identity_ok=True,
                     finish_reason="stop", status="ok", server_id="s1",
                     attempts=[])
        spent, held, n, corrupt = led.totals()
        check("completed spends", (spent, n) == (0.001, 2))
        try:
            led.reserve("r3", "m", "tb1", "t", 300, 100)
            check("request cap trips", False)
        except budget_mod.BudgetExceeded:
            check("request cap trips", True)
        # caps survive restart (same file, new object)
        led2 = budget_mod.Ledger(Path(tmp) / "l.jsonl", 0.01, 5, PRICING)
        spent, held, n, corrupt = led2.totals()
        check("ledger persists", (spent, n) == (0.001, 2))
        try:
            led2.reserve("r9", "m", "tb1", "t", 300000, 100000)
            check("usd cap trips", False)
        except budget_mod.BudgetExceeded:
            check("usd cap trips", True)


def test_identity():
    check("exact", vultr.identities_match("a", "a"))
    check("normalize suffix rejected (undocumented)",
          not vultr.identities_match("a", "a-normalize"))
    check("normalize suffix rejected reverse",
          not vultr.identities_match("a-normalize", "a"))
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


def test_redact():
    # Fixtures are assembled from fragments: no literal credential
    # shape may sit in this file (I/O scrubbers mask Bearer/AKIA/JWT
    # shapes in transit, which would make a literal fixture test the
    # scrubber instead of the redactor).
    tok = "abc" + "123"
    check("Bearer token",
          redact_mod.redact("Authorization: Bearer " + tok) ==
          "Authorization: [REDACTED]")
    akia = "AK" + "IA" + "IOSFODNN7EXAMPLE"
    check("akia masked",
          redact_mod.redact("key " + akia + " here") ==
          "key [REDACTED] here")
    jwt = "eyJ" + "hbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.sig"
    check("jwt masked", "[REDACTED]" in redact_mod.redact(
        "t " + jwt + " here"))
    check("pem masked", "[REDACTED]" in redact_mod.redact(
        "k -----BEGIN RSA PRIVATE KEY-----\nMIIB\n-----END RSA PRIVATE "
        "KEY----- e"))
    check("password assignment masked",
          redact_mod.redact("db password=" + "hunter2 ok") ==
          "db password=[REDACTED] ok")
    check("api key masked",
          redact_mod.redact("x api_key: " + tok + " y") ==
          "x api_key: [REDACTED] y")
    check("token subject untouched",
          redact_mod.redact("token file | config/token.txt | -") ==
          "token file | config/token.txt | -")
    check("tsv structure kept",
          redact_mod.redact("s | f | - | f | pwd=" + "hunter2 | g.md:1"
                            " | OK") ==
          "s | f | - | f | pwd=[REDACTED] | g.md:1 | OK")


if __name__ == "__main__":
    test_ledger()
    test_identity()
    test_verdict()
    test_no_secret_paths()
    test_redact()
    print(f"{PASS} harness checks passed, ALL GREEN (offline)")
