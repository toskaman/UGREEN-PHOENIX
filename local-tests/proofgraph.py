"""Proof Graph + Readiness Passport renderer (local dev tooling).

Renders the designs in ``proof-graph.md`` and ``readiness-passport.md``
from a ``harness.run()`` result dict. This is NOT part of the submitted
Skill: on the NAS the knowledge-agent serializes the same text from the
same findings. Local simulation only — proves nothing about Uliya.

Public API:
  build_graph(result) -> (nodes, edges)
  format_graph(nodes, edges) -> str
  render_graph(result) -> str
  render_delta_graph(result) -> str  (requires result["delta"])
  render_passport(result, project, scope, scenario, version,
                  assessed_at="not recorded") -> str
  check_consistency(result) -> list[str]  (empty == consistent)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness
from harness import (CONFLICTING, FOUND, INACCESSIBLE, NOT_FOUND, UNKNOWN,
                     redact)

REQ, DOC, FILE, FACT, GAP, CLASH = "REQ", "DOC", "FILE", "FACT", "GAP", "CLASH"

ANTI_GUARANTEE = (
    "> This passport documents EVIDENCE REVIEWED, not a tested recovery.\n"
    "> It expires the moment the scope changes. Only a real restoration\n"
    "> test proves recoverability.")


def _constraint(e):
    if e.get("op") and e.get("version"):
        return f" {e['op']} {e['version']}"
    return ""


def build_graph(result):
    """Build (nodes, edges) from harness evidence. Every edge cites a
    path:line visible in the result; GAP/CLASH nodes are never dropped."""
    nodes, edges = [], []
    for e in result["evidence"]:
        req = f"[REQ: {redact(e['subject'])}{_constraint(e)}]"
        doc = f"[DOC: {e['source']}:{e['line']}]"
        nodes += [req, doc]
        edges.append((req, "stated-by", doc))
        status = e["status"]
        if status == FOUND:
            # v9: a version-constrained dotted subject is a capability
            # (FACT), not a file — mirrors harness capability handling.
            if "/" in e["subject"] or ("." in e["subject"]
                                       and not e.get("op")):
                target = f"[FILE: {redact(e['subject'])}]"
            else:
                target = f"[FACT: {redact(e['detail'])}]"
            nodes.append(target)
            edges.append((req, "satisfied-by", target))
        elif status == CONFLICTING:
            clash = f"[CLASH: {redact(e['detail'])}]"
            nodes.append(clash)
            edges.append((req, "contested", clash))
        else:  # NOT_FOUND, INACCESSIBLE, UNKNOWN
            gap = f"[GAP: {redact(e['subject'])} — {status}: {redact(e['detail'])}]"
            nodes.append(gap)
            edges.append((req, "blocked-by", gap))
    return nodes, edges


def format_graph(nodes, edges):
    """Serialize (nodes, edges) to the canonical text format."""
    uniq = list(dict.fromkeys(nodes))
    lines = [f"PROOF GRAPH ({len(uniq)} nodes, {len(edges)} edges)"]
    by_req = {}
    for src, kind, dst in edges:
        by_req.setdefault(src, []).append((kind, dst))
    for req, links in by_req.items():
        lines.append(req)
        for kind, dst in links:
            lines.append(f"  --{kind}--> {dst}")
    gaps = sum(1 for _, k, _ in edges if k == "blocked-by")
    clashes = sum(1 for _, k, _ in edges if k == "contested")
    lines.append(f"UNRESOLVED: {gaps} gap{'s' if gaps != 1 else ''}, "
                 f"{clashes} clash{'es' if clashes != 1 else ''}.")
    return "\n".join(lines)


def render_graph(result):
    return format_graph(*build_graph(result))


def render_delta_graph(result):
    """Re-emit the graph with per-node Recovery Delta states."""
    delta = result.get("delta")
    if not delta:
        raise ValueError("no delta in result: run harness with prior=")
    state_of = {t["subject"]: t["state"] for t in delta["transitions"]}
    nodes, edges = build_graph(result)
    lines = [f"PROOF GRAPH WITH DELTA "
             f"({delta['prior_verdict']} -> {delta['verdict']})"]
    by_req = {}
    for src, kind, dst in edges:
        by_req.setdefault(src, []).append((kind, dst))
    subjects = [e["subject"] for e in result["evidence"]]
    req_state = {}
    for e in result["evidence"]:
        req = f"[REQ: {redact(e['subject'])}{_constraint(e)}]"
        req_state[req] = state_of.get(e["subject"], "NEW")
    for req, links in by_req.items():
        lines.append(f"{req} [{req_state.get(req, 'UNVERIFIED')}]")
        for kind, dst in links:
            lines.append(f"  --{kind}--> {dst}")
    for t in delta["transitions"]:
        if t["subject"] not in subjects:
            lines.append(f"[REQ: {redact(t['subject'])}] [{t['state']}] "
                         f"(prior-only: {t['previous']} -> {t['current']})")
    lines.append(f"Documentary blockers resolved: {delta['resolved_count']}. "
                 "This is not a tested restoration.")
    return "\n".join(lines)


def render_passport(result, project, scope, scenario, version,
                    assessed_at="not recorded"):
    """Render the 7-section Readiness Passport + anti-guarantee."""
    cov = result["coverage"]
    blockers = [e for e in result["evidence"]
                if e["status"] in (NOT_FOUND, CONFLICTING)]
    lines = ["# Recovery Readiness Passport", "",
             "## 1. Identity",
             f"Project: {project} | Scope: {scope} | Scenario: {scenario}",
             f"Assessed: {assessed_at} | PHOENIX: {version} "
             "(local simulation, not a NAS result).", "",
             "## 2. Verdict", result["verdict"], "",
             "## 3. Requirements (Proof Graph)", render_graph(result), "",
             "## 4. Evidence limits",
             f"Reviewed: {len(cov['reviewed'])}, skipped: "
             f"{len(cov['skipped'])}, inaccessible: "
             f"{len(cov['inaccessible'])}, truncated: "
             f"{len(cov['truncated'])}, errors: {len(cov['errors'])}, "
             f"depth-capped: {cov['depth_capped']}.",
             f"Completion: {result['completion']}."]
    if result["delta"] is not None:
        # v9: contract keeps §§5-6 separate (delta graph, then history).
        lines += ["", "## 5. Blockers (prioritized)",
                  render_delta_graph(result), "",
                  "## 6. Resolution history"]
        lines += [f"- {redact(t['subject'])}: {t['previous']} -> "
                  f"{t['current']} [{t['state']}]"
                  for t in result["delta"]["transitions"]]
    else:
        lines += ["", "## 5. Blockers (prioritized)"]
        lines += [f"- P1: {redact(e['subject'])}: {e['status']} — "
                  f"{redact(e['detail'])}" for e in blockers] or ["- none"]
        lines += ["", "## 6. Resolution history",
                  "None — first assessment. Supply this passport as prior "
                  "on recheck to obtain a Recovery Delta."]
    lines += ["", "## 7. Next checks",
              "This passport expires if the scope changes: new files, "
              "version changes, moved folders, or permission changes "
              "require a fresh assessment.", "",
              ANTI_GUARANTEE]
    return "\n".join(lines)


def check_consistency(result, model=None):
    """Verify graph/evidence-table agreement. Returns issue list.
    model is an optional (nodes, edges) pair to audit instead of the
    freshly built graph (used to prove tampering is detected)."""
    issues = []
    nodes, edges = model if model is not None else build_graph(result)
    subjects = [e["subject"] for e in result["evidence"]]
    for e in result["evidence"]:
        req = f"[REQ: {redact(e['subject'])}{_constraint(e)}]"
        if req not in nodes:
            issues.append(f"missing REQ node for {e['subject']!r}")
        kinds = [k for s, k, _ in edges if s == req]
        if "stated-by" not in kinds:
            issues.append(f"missing stated-by edge for {e['subject']!r}")
        want = ("satisfied-by" if e["status"] == FOUND
                else "contested" if e["status"] == CONFLICTING
                else "blocked-by")
        if want not in kinds:
            issues.append(f"missing {want} edge for {e['subject']!r} "
                          f"(status {e['status']})")
    rendered_reqs = {s for s, _, _ in edges}
    for req in rendered_reqs:
        if req not in nodes:
            issues.append(f"dangling edge source {req!r}")
    # every edge target of GAP/CLASH kind must exist (never dropped)
    for _, kind, dst in edges:
        if kind in ("blocked-by", "contested") and dst not in nodes:
            issues.append(f"dropped {kind} target {dst!r}")
    if sum(1 for _, k, _ in edges if k == "stated-by") != len(subjects):
        issues.append("stated-by edge count diverges from evidence count")
    return issues


if __name__ == "__main__":
    res = harness.run(Path(sys.argv[1]))
    print(render_passport(res, project=sys.argv[1], scope=res["scope"],
                          scenario="local demo", version="dev"))
