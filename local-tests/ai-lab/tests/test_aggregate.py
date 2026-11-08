"""Offline tests for Arch B deterministic aggregation (no network).

Usage (from repo root): python local-tests/ai-lab/tests/test_aggregate.py
"""

import sys
from pathlib import Path

AI_LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_LAB))

from evaluators import aggregate as agg
from evaluators import delta as delta_mod
from evaluators import normalize as norm_mod
from evaluators import verify as ver

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
    # v6: malformed (thinking-chatter) rows -> UNKNOWN, never a vote
    check("chatter req abstains", agg.aggregate(
        "plates | the plates folder | - | MISSING | - | g.md:1 | OK")
        ["findings"][0]["label"] == "UNKNOWN")
    check("chatter obs abstains", agg.aggregate(
        "s | f | - | <option B> | x | g.md:1 | OK")
        ["findings"][0]["label"] == "UNKNOWN")
    check("suspect excluded from conflict", agg.aggregate(
        "s | f | 3 or newer | c/f | v 5 | g.md:1 | OK\n"
        "s | bad req | exactly 9 | c/f | v 5 | g.md:2 | OK")
        ["verdict"] == INSUF)  # FOUND + suspect-UNKNOWN, no conflict
    # v6: known= citation resolution (F5)
    known = {"g.md": 5, "f.txt": 2}
    check("forged cite dropped", agg.aggregate(
        "s | f | - | f | x | nope/x.md:9 | OK", known=known)
        ["verdict"] == INSUF)
    check("misaddressed line dropped", agg.aggregate(
        "s | f | - | f | x | g.md:99 | OK", known=known)
        ["verdict"] == INSUF)
    check("resolved cite scores", agg.aggregate(
        "s | f | - | f | x | g.md:3 | OK", known=known)
        ["verdict"] == CLEAR)
    check("no-known backward compat", agg.aggregate(
        "s | f | - | f | x | g.md:99 | OK")["verdict"] == CLEAR)
    # v6: delta path anchoring (F2/F4)
    cur_clear = {"verdict": CLEAR, "findings": [
        {"subject": "token banner", "label": "FOUND",
         "req_path": "web/banner.txt", "obs_path": "web/banner.txt",
         "sources": "web/banner.txt:1"}]}
    check("single shared word never resolves", delta_mod.compute(
        B, [{"subject": "token file", "path": "config/token.txt"}],
        cur_clear)["deltas"][0]["state"] == "STILL UNCERTAIN")
    cur_matched = {"verdict": CLEAR, "findings": [
        {"subject": "seed check", "label": "FOUND",
         "req_path": "config/seed.txt", "obs_path": "config/seed.txt",
         "sources": "config/seed.txt:1"}]}
    check("path-anchored match resolves", delta_mod.compute(
        B, [{"subject": "seed file", "path": "config/seed.txt"}],
        cur_matched)["deltas"][0]["state"] == "RESOLVED")
    check("vanish + clear stays uncertain", delta_mod.compute(
        B, [{"subject": "seed file", "path": "config/seed.txt"}],
        cur_clear)["deltas"][0]["state"] == "STILL UNCERTAIN")
    check("vanish + nonclear stays uncertain", delta_mod.compute(
        B, [{"subject": "seed file", "path": "config/seed.txt"}],
        {"verdict": INSUF, "findings": []})["deltas"][0]["state"]
        == "STILL UNCERTAIN")
    # v6: rowfix re-verified before merge (F3)
    base = ("dashboard port | - | - | config/service.txt:1 | port 9090 | "
            "docs/guide.md:3 | OK")
    forged = ["evil | f | - | nope/missing.txt | pwned | nope/missing.txt:1"
              " | OK"]
    check("fabricated rowfix dropped",
          "pwned" not in ver.merge_rowfix("tb1", base, forged,
                                          dataset="trackb"))
    good = ["shot | scenes/shot01.blend | - | scenes/shot01.blend | BLEND | "
            "scenes/shot01.blend:1 | OK"]
    check("verified rowfix appended",
          "BLEND" in ver.merge_rowfix("tb1", base, good,
                                      dataset="trackb"))
    # v6 adversarial TSV matrix a1-a15 (multilingual constraints)
    def row(c, v):
        return (f"s | f | {c} | c/f | {v} | g.md:1 | OK")
    check("a1 inclusive le endpoint", agg.aggregate(
        row("up to 5", "v 5"))["verdict"] == CLEAR)
    check("a2 strict lt endpoint", agg.aggregate(
        row("up to but not including 5", "v 5"))["verdict"] == B)
    check("a3 bare vs port noise abstains", agg.aggregate(
        row("8080", "service on 8080 (pid 12)"))["verdict"] == INSUF)
    check("a4 fr strict gt boundary", agg.aggregate(
        row("Doit être > 2", "v 2"))["verdict"] == B)
    check("a5 fr range endpoint", agg.aggregate(
        row("entre 2.0 et 4.2", "v 4.2"))["verdict"] == CLEAR)
    check("a6 series satisfies", agg.aggregate(
        row("serie 2.x", "v 2.7"))["verdict"] == CLEAR)
    check("a7 contradictory cues abstain", agg.aggregate(
        row("exactly 2 or newer", "v 3"))["verdict"] == INSUF)
    check("a8 decimal comma abstains", agg.aggregate(
        row("version 2,4", "v 2"))["verdict"] == INSUF)
    check("a9 vague observed abstains", agg.aggregate(
        row("format 6", "moved to archive/latest"))["verdict"] == INSUF)
    check("a10 exclusion asymmetry", agg.aggregate(
        row("up to 5", "v 5"))["verdict"] == CLEAR and agg.aggregate(
        row("up to but not including 5", "v 5"))["verdict"] == B)
    check("a11 folded uppercase fr", agg.aggregate(
        row("OU SUPÉRIEUR 2", "v 3"))["verdict"] == CLEAR)
    check("a12 edition noise tolerated", agg.aggregate(
        row("at least 4", "edition 4"))["verdict"] == CLEAR)
    check("a13 padded semver equal", agg.aggregate(
        row("exactly 2.4", "v 2.4.0"))["verdict"] == CLEAR)
    check("a14 headline beats patch note", agg.aggregate(
        row("3 or newer", "v 3, patch 2 applied"))["verdict"] == CLEAR)
    check("a15 fr alt relief", agg.aggregate(
        "job | a/full | 2 ou superieur | MISSING | - | g.md:1 | OK\n"
        "job | a/incr | 2 ou superieur | a/incr | v 3 | g.md:2 | OK\n"
        "ALT | sauvegarde | a/full | a/incr")["verdict"] == CLEAR)
    # v6 pinned normalizer contract (constraint, observed -> outcome)
    contract = [
        ("2 or newer", "portal schema 3", "SATISFIED"),
        ("shop schema 2 ou plus récent", "shop schema 4", "SATISFIED"),
        ("Le cache doit déclarer format 4 ou supérieur", "cache format 2",
         "VIOLATED"),
        ("gateway must be 6 or older", "gateway 5.1", "SATISFIED"),
        ("doit etre version 3 ou anterieure", "notificateur version 4",
         "VIOLATED"),
        ("must be exactly 2.4.1", "archiver 2.4.1", "SATISFIED"),
        ("doit etre exactement 1.9", "rendu 1.10", "VIOLATED"),
        ("between 2.0 and 3.5", "metrics 3.1", "SATISFIED"),
        ("doit etre entre 2 et 4", "sauvegarde 5", "VIOLATED"),
        ("must be newer than 2 (2 excluded)", "search 2", "VIOLATED"),
        ("doit etre strictement inferieur a 3", "auth 3", "VIOLATED"),
        ("must declare layout 6", "dispatcher layout 5", "UNKNOWN"),
        ("doit declarer protocole 3", "protocole: a confirmer", "UNKNOWN"),
        ("> 2", "v 2", "VIOLATED"), (">= 2", "v 2", "SATISFIED"),
        ("< 3", "v 3", "VIOLATED"), ("<= 3", "v 3", "SATISFIED"),
        ("entre 2 et 4", "v 4", "SATISFIED"),
        ("entre 2 et 4", "v 5", "VIOLATED"),
        ("2.x", "v 2.7", "SATISFIED"), ("2.x", "v 3.0", "VIOLATED"),
        ("format 6", "latest", "UNKNOWN"),
        ("2 ou superieur", "v 10.1", "SATISFIED"),
        ("format 6", "format 6", "SATISFIED"),
        ("at least 4", "v 3", "VIOLATED"),
        ("minimum 2", "v 2", "SATISFIED"),
        ("3+", "v 4", "SATISFIED"), ("no newer than 5", "v 6", "VIOLATED"),
        ("version 3 minimum, version 6 exclue", "v 6", "VIOLATED"),
        ("version 3 minimum, version 6 exclue", "v 4", "SATISFIED"),
        ("schema 3", "port 8080 schema 2", "UNKNOWN"),
        ("schema exactly 3", "port 8080 schema 2", "VIOLATED"),
        ("compatible with 2.x", "v 2.5", "SATISFIED"),
        ("version inferieure a 5", "v 5", "VIOLATED"),
        ("versions 2 à 4 incluses", "v 3", "SATISFIED"),
        # v6 red-team: negation exclusions (false-clear fixes)
        ("must not be 5", "v 5", "VIOLATED"),
        ("must not be 5", "v 6", "SATISFIED"),
        ("not including versions 5 and 6", "v 6", "VIOLATED"),
        ("not including versions 5 and 6", "v 7", "SATISFIED"),
        ("versions 5 et 6 exclues", "v 5", "VIOLATED"),
        ("versions 5, 6 exclues", "v 6", "VIOLATED"),
        ("version 5 (4 excluded)", "v 5", "SATISFIED"),
        ("version 5 (4 excluded)", "v 6", "UNKNOWN"),
        ("except 5", "v 5", "VIOLATED"),
        ("version different from 5", "v 5", "VIOLATED"),
        ("ne doit pas etre 5", "v 5", "VIOLATED"),
        ("not including 5", "v 7", "SATISFIED"),
        ("requires 2, version 6 exclue", "v 2", "SATISFIED"),
        ("requires 2, version 6 exclue", "v 6", "VIOLATED"),
        ("at least 2, not including 5", "v 5", "VIOLATED"),
        ("at least 2, not including 5", "v 3", "SATISFIED"),
        ("version \u2265 4", "v 5", "SATISFIED"),
        ("version \u2264 4", "v 3", "SATISFIED"),
        ("version \u2260 5", "v 5", "VIOLATED"),
        # v6 purple: chain guard + colon form (regression pins)
        ("excluded: 5, 6 and 7", "v 7", "VIOLATED"),
        ("must be 5, 6 excluded", "v 5", "SATISFIED"),
        ("must be 5, 6 excluded", "v 6", "VIOLATED"),
        ("5, 6, 7 excluded", "v 8", "SATISFIED"),
        ("schema 2 ou superieur, sauf 3", "v 3", "VIOLATED"),
        # v7: XOR exclusivity (was ANTI-XOR: rejected members, cleared other)
        ("version 5 or 6 but not both", "v 5", "SATISFIED"),
        ("version 5 or 6 but not both", "v 7", "VIOLATED"),
        ("version 5 ou 6 mais pas les deux", "v 6", "SATISFIED"),
        ("version 5 ou 6 mais pas les deux", "v 7", "VIOLATED"),
        # v7 purple: XOR + third exclusion or bound is contradictory
        ("version 5 or 6 but not both, 7 excluded", "v 5", "UNKNOWN"),
        ("at least 5 or 6 but not both", "v 5", "UNKNOWN"),
        # v7: conditional markers abstain (condition unexamined, never BARE)
        ("version 5 unless legacy mode", "v 5", "UNKNOWN"),
        ("version 5 sauf si mode legacy", "v 5", "UNKNOWN"),
        ("version 5 only if clean install", "v 5", "UNKNOWN"),
        ("version 5 uniquement si install propre", "v 5", "UNKNOWN"),
        ("use 5 if node count is 2", "v 5", "UNKNOWN"),
        ("version 5 when cluster mode", "v 5", "UNKNOWN"),
        ("version 5 a moins que mode legacy", "v 5", "UNKNOWN"),
    ]
    for i, (c, o, exp) in enumerate(contract):
        n = norm_mod.normalize_constraint(c)
        code, _ = norm_mod.compare(
            n, norm_mod.pick_observed(c, o,
                                     norm_op=n["op"] if n else None))
        check(f"norm-case-{i:02d}", code == exp,
              f"{ascii(c)} vs {ascii(o)} -> {code}, want {exp}")
    # v6 truncation grounding (model TRUNC needs byte confirmation)
    check("tb5 net flags marked guide",
          "docs/guide.md" in ver.truncated_docs("tb5", "trackb"))
    check("short config not prose-flagged",
          not ver._prose_shaped(["port 9090"]))
    check("unconfirmed model trunc dropped", agg.aggregate(
        "s | f | - | f | x | g.md:1 | OK\n"
        "TRUNC | g.md | model says so",
        truncated_docs=set())["findings"][0]["label"] == "FOUND")
    check("confirmed trunc abstains", agg.aggregate(
        "s | f | - | f | x | g.md:1 | OK\n"
        "TRUNC | g.md | model says so",
        truncated_docs={"g.md"})["findings"][0]["label"] == "UNKNOWN")
    check("keyword needs byte confirmation", agg.aggregate(
        "s | f | - | f | x | g.md:1 | TRUNCATED evidence",
        truncated_docs=set())["findings"][0]["label"] == "FOUND")
    print(f"{PASS} aggregation checks passed, ALL GREEN (offline)")
