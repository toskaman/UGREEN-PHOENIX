"""Proof Graph / Passport tests (offline, deterministic).

Validates the renderer in proofgraph.py against the designs in
proof-graph.md and readiness-passport.md: format conformance,
citation discipline, GAP/CLASH retention, report/graph agreement,
delta states, passport sections, redaction, determinism.
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness
import proofgraph
from harness import redact

HERE = Path(__file__).resolve().parent
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [ok] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))


def make_scope(files):
    tmp = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp


# --- 1. header counts match the built model -------------------------------
res_a = harness.run(HERE / "corpus" / "core-a")
nodes, edges = proofgraph.build_graph(res_a)
graph = proofgraph.render_graph(res_a)
m = re.match(r"PROOF GRAPH \((\d+) nodes, (\d+) edges\)", graph)
check("graph-a: header present", m is not None)
if m:
    check("graph-a: node count exact",
          int(m.group(1)) == len(set(nodes)),
          f"header {m.group(1)} vs {len(set(nodes))}")
    check("graph-a: edge count exact",
          int(m.group(2)) == len(edges),
          f"header {m.group(2)} vs {len(edges)}")

# --- 2. citation discipline: every edge target is grounded ----------------
doc_targets = [d for _, k, d in edges if k == "stated-by"]
check("graph-a: every stated-by cites path:line",
      all(re.fullmatch(r"\[DOC: \S+:\d+\]", d) for d in doc_targets),
      str(doc_targets))
fact_targets = [d for _, k, d in edges if k == "satisfied-by"]
check("graph: satisfied-by edges grounded (FILE or cited FACT)",
      all(d.startswith("[FILE: ") or re.search(r"\S+:\d+ \([^)]*\)", d)
          for d in fact_targets),
      str(fact_targets))
res_b = harness.run(HERE / "corpus" / "core-b")
_, edges_b = proofgraph.build_graph(res_b)
clash_targets = [d for _, k, d in edges_b if k == "contested"]
check("graph-b: conflict keeps a CLASH node with both sources",
      len(clash_targets) == 1 and "contradicts" in clash_targets[0]
      and re.search(r"\S+:\d+", clash_targets[0]) is not None,
      str(clash_targets))
gap_targets = [d for _, k, d in edges if k == "blocked-by"]
check("graph-a: missing asset keeps a GAP node",
      len(gap_targets) >= 1 and all("NOT FOUND" in g for g in gap_targets),
      str(gap_targets))

# --- 3. report/graph agreement: same finding set, two render paths --------
for res, tag in ((res_a, "a"), (res_b, "b")):
    g = proofgraph.render_graph(res)
    missing_g = [e["subject"] for e in res["evidence"]
                 if redact(e["subject"]) not in g]
    missing_r = [e["subject"] for e in res["evidence"]
                 if redact(e["subject"]) not in res["report"]]
    check(f"agree-{tag}: every finding in graph", not missing_g,
          str(missing_g))
    check(f"agree-{tag}: every finding in report", not missing_r,
          str(missing_r))
    check(f"agree-{tag}: checker clean",
          proofgraph.check_consistency(res) == [],
          str(proofgraph.check_consistency(res)))

# --- 4. tamper detection ----------------------------------------------------
tampered_nodes = [n for n in nodes if not n.startswith("[GAP:")]
tampered_edges = [(s, k, d) for s, k, d in edges
                  if not d.startswith("[GAP:")]
issues = proofgraph.check_consistency(res_a,
                                      (tampered_nodes, tampered_edges))
check("tamper: dropped GAP detected",
      any("blocked-by" in i for i in issues), str(issues))

# --- 5. delta graph ---------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp) / "a"
    shutil.copytree(HERE / "corpus" / "core-a", t)
    before = harness.run(t)
    (t / "config").mkdir(parents=True, exist_ok=True)
    (t / "config" / "prod-config.yaml").write_text("# fix\n",
                                                  encoding="utf-8")
    after = harness.run(t, prior=before)
    dg = proofgraph.render_delta_graph(after)
    check("delta: resolved subject tagged RESOLVED",
          "[RESOLVED]" in dg, dg.splitlines()[0] if dg else "")
    check("delta: verdict transition shown",
          "DOCUMENTARY BLOCKER IDENTIFIED -> " in dg, dg)
    states = {tr["state"] for tr in after["delta"]["transitions"]}
    check("delta: every transition state rendered",
          all(f"[{s}]" in dg or s in dg for s in states), str(states))
    try:
        proofgraph.render_delta_graph(before)
        check("delta: no-delta raises", False, "no error")
    except ValueError:
        check("delta: no-delta raises", True)

# prior-only subject is kept, never silently dropped
prior = {"verdict": "DOCUMENTARY BLOCKER IDENTIFIED", "scope": "core-a",
         "evidence": [{"subject": "ghost/old.yaml", "status": "NOT FOUND IN SCOPE",
                       "detail": "was missing"}]}
res_prior = harness.run(HERE / "corpus" / "core-a", prior=prior)
dg2 = proofgraph.render_delta_graph(res_prior)
check("delta: prior-only subject kept with UNVERIFIED",
      "ghost/old.yaml" in dg2 and "UNVERIFIED" in dg2, dg2)

# --- 6. passport ------------------------------------------------------------
pp = proofgraph.render_passport(res_a, project="demo", scope="core-a",
                                scenario="missing asset", version="v6test")
for n in ("1. Identity", "2. Verdict", "3. Requirements", "4. Evidence",
          "5. Blockers", "6. Resolution", "7. Next"):
    check(f"passport: section {n} present", n in pp)
check("passport: anti-guarantee verbatim",
      "not a tested recovery" in pp and "expires the moment" in pp)
check("passport: default timestamp honest",
      "not recorded" in pp, pp)
pp2 = proofgraph.render_passport(res_a, project="d", scope="s",
                                 scenario="x", version="v",
                                 assessed_at="2026-11-08")
check("passport: explicit timestamp used", "2026-11-08" in pp2)
check("passport: first-assessment history note",
      "first assessment" in pp.lower(), pp)
pp3 = proofgraph.render_passport(res_prior, project="d", scope="s",
                                 scenario="x", version="v")
check("passport: delta embedded when present",
      "PROOF GRAPH WITH DELTA" in pp3)

# --- 7. redaction ------------------------------------------------------------
scope = make_scope({"guide.md": "REQUIRES: api_key=hunter2\n"})
res_s = harness.run(scope)
g_s = proofgraph.render_graph(res_s)
p_s = proofgraph.render_passport(res_s, project="d", scope="s",
                                 scenario="x", version="v")
check("redact: secret absent from graph", "hunter2" not in g_s, g_s)
check("redact: secret absent from passport", "hunter2" not in p_s)
shutil.rmtree(scope, ignore_errors=True)

# --- 8. footer grammar ------------------------------------------------------
check("grammar: singular gap", "1 gap," in graph and "1 gaps" not in graph,
      graph.splitlines()[-1])
check("grammar: zero clashes",
      "0 clashes." in graph, graph.splitlines()[-1])

# --- 9. determinism ----------------------------------------------------------
check("determinism: graph stable",
      proofgraph.render_graph(res_a) == proofgraph.render_graph(res_a))
check("determinism: passport stable",
      proofgraph.render_passport(res_a, project="d", scope="s",
                                 scenario="x", version="v")
      == proofgraph.render_passport(res_a, project="d", scope="s",
                                     scenario="x", version="v"))

print(f"\n{PASS} proofgraph checks passed"
      + (f", {FAIL} FAILED" if FAIL else ", ALL GREEN (offline)"))
sys.exit(1 if FAIL else 0)
