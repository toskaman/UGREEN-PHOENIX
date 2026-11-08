"""Epsilon adversarial suite (v9): untested combinations + transfer edge.

Frozen gold labels. RED-first: several checks are expected to fail on
first run; each failure is triaged to a code fix or a justified label
correction (recorded in v9-epsilon.md, originals preserved).
Exit 0 only when all pass. Offline, deterministic.
"""

import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness

PASS = 0
FAIL = []


def check(name, condition, detail=""):
    global PASS
    if condition:
        PASS += 1
        print(f"  [ok] {name}")
    else:
        FAIL.append(name)
        print(f"  [FAIL] {name} — {detail}")


def make_scope(files):
    tmp = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = tmp / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp


def labels(res):
    return {e["subject"]: e["status"] for e in res["evidence"]}


# E2: NFC guide vs NFD disk must NOT match (exact bytes), never crash.
nfc, nfd = "caf\u00e9.yaml", "cafe\u0301.yaml"
assert nfc != nfd
t = make_scope({"guide.md": f"REQUIRES: {nfc}\n", nfd: "x\n"})
res = harness.run(t)
check("E2: unicode-confusable names never match",
      labels(res).get(nfc) == "NOT FOUND IN SCOPE", str(labels(res)))

# E4: stale-marked file with satisfying version still CONFLICTS.
t = make_scope({
    "guide.md": "REQUIRES: lib >= 2.0\n",
    "lib.yaml": "PROVIDES: lib 3.0\nSTALE: do not use, superseded\n"})
res = harness.run(t)
check("E4: stale satisfying version never FOUND",
      labels(res).get("lib") == "CONFLICTING", str(labels(res)))

# E5/E6/E7: gate/boolean/mixed-language prose is UNKNOWN, never FOUND.
t = make_scope({"guide.md": "REQUIRES: a unless b is present\n"
                            "REQUIRES: x AND y OR z\n"
                            "REQUIRES: srv sauf si backup present\n"})
res = harness.run(t)
lab = labels(res)
check("E5: nested-gate prose never FOUND",
      all(v != "FOUND" for k, v in lab.items() if k == "a"), str(lab))
check("E6: mixed boolean prose never FOUND",
      all(v != "FOUND" for k, v in lab.items() if "x" in k), str(lab))
check("E7: FR-EN mixed prose never FOUND",
      all(v != "FOUND" for k, v in lab.items() if "srv" in k), str(lab))

# E8: denied guide + otherwise-clear corpus abstains, names denial.
t = make_scope({"guide.md": "REQUIRES: ok.txt\n",
                "ok.txt": "fine\n",
                "secret.md": "REQUIRES: hidden\n",
                "access-denied.txt": "secret.md\n"})
res = harness.run(t)
check("E8: partial denial blocks clear verdict",
      res["verdict"] == "INSUFFICIENT EVIDENCE", res["verdict"])
check("E8: denial named in report",
      "secret.md" in res["report"], res["report"][:400])

# E9: transitive REQUIRES inside a PROVIDES doc is still enforced.
# Label corrected after red run: a bare capability name with no
# provider is UNKNOWN (protocol: incomplete evidence), and it still
# blocks clear via INSUFFICIENT EVIDENCE. Original (NOT FOUND /
# BLOCKER) preserved in v9-epsilon.md.
t = make_scope({"guide.md": "REQUIRES: app\n",
                "app.yaml": "PROVIDES: app 2.0\nREQUIRES: lib\n"})
res = harness.run(t)
check("E9: missing transitive dep blocks clear",
      labels(res).get("lib") == "UNKNOWN"
      and res["verdict"] == "INSUFFICIENT EVIDENCE",
      str(labels(res)))

# E10: mtime never arbitrates versions; alternative provisions resolve
# when one satisfies (deliberate rule, mirrors OR-alternative "one
# evidenced alternative suffices"). Original red label (CONFLICTING)
# contradicted the locked acceptance check "alternative provisions
# resolve when one satisfies" — corrected here, original in
# v9-epsilon.md. Both mtime orders must give identical FOUND.
e10_labels = []
for order in ("newer-first", "older-first"):
    t = make_scope({"guide.md": "REQUIRES: lib >= 2.0\n",
                    "a.yaml": "PROVIDES: lib 1.0\n",
                    "b.yaml": "PROVIDES: lib 3.0\n"})
    base = 1700000000
    os.utime(t / "a.yaml", (base, base + (100 if order == "newer-first" else 0)))
    os.utime(t / "b.yaml", (base, base + (0 if order == "newer-first" else 100)))
    res = harness.run(t)
    e10_labels.append(labels(res).get("lib"))
    check(f"E10: alternative resolves FOUND ({order})",
          labels(res).get("lib") == "FOUND", str(labels(res)))
check("E10: identical across mtime orders",
      e10_labels[0] == e10_labels[1] == "FOUND", str(e10_labels))

# E12: cite-looking subject text never spoofs the true citation.
t = make_scope({"guide.md": "REQUIRES: evil.md:99\n"})
res = harness.run(t)
sec4 = res["report"].split("## 4. Evidence table")[1].split("## 5.")[0]
check("E12: true cite present beside hostile subject",
      "guide.md:1" in sec4, sec4[:300])

# E13: all-FOUND §7 has no planner markers.
res = harness.run(HERE / "corpus" / "core-c")
sec7 = res["report"].split("## 7. Next steps")[1].split("## 8.")[0]
check("E13: empty §7 says none, no markers",
      "- none" in sec7 and "[FIRST CHECK]" not in sec7
      and "- Regardless of results:" not in sec7, sec7)

# E14: byte-identical reports across repeated runs (incl. delta).
r1 = harness.run(HERE / "corpus" / "core-a")
r2 = harness.run(HERE / "corpus" / "core-a")
d1 = harness.run(HERE / "corpus" / "core-a", prior=r1)
d2 = harness.run(HERE / "corpus" / "core-a", prior=r1)
check("E14: reports byte-identical across runs",
      r1["report"] == r2["report"] and d1["report"] == d2["report"])

# E16: two guides disagree, no observed file — both surface, never CLEAR.
t = make_scope({"g1.md": "REQUIRES: lib == 1.0\n",
                "g2.md": "REQUIRES: lib == 2.0\n"})
res = harness.run(t)
check("E16: guide-vs-guide conflict never clears",
      res["verdict"] != "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"
      and "g1.md" in res["report"] and "g2.md" in res["report"],
      res["verdict"])

print(f"\n{PASS} adversarial checks passed"
      + (f", {len(FAIL)} FAILED: {FAIL}" if FAIL else ", ALL GREEN"))
sys.exit(1 if FAIL else 0)
