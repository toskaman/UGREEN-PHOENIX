"""Beta: evidence-based selection among 4 §7 (Next steps) variants.

Each generator maps a harness result to action lines. All run on the 8
frozen corpora; metrics are coverage, groundedness, criterion presence,
and size. Verdicts are never touched (asserted identical). Dev-only.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))

import harness
from harness import (CONFLICTING, FOUND, INACCESSIBLE, NOT_FOUND, UNKNOWN,
                     redact)

CORPORA = ["core-a", "core-b", "core-c", "core-d", "edge", "edge-2",
           "edge-3", "scale"]
ACTIONABLE = (NOT_FOUND, CONFLICTING, INACCESSIBLE, UNKNOWN)

ACTION = {
    NOT_FOUND: "Ask the operator to supply '{s}' or point to its "
               "approved location",
    CONFLICTING: "Confirm the intended '{s}' version with the "
                 "document owners",
    INACCESSIBLE: "Request read access to '{s}' or an approved copy",
    UNKNOWN: "Resolve the '{s}' evidence gap with a clearer source",
}
RESOLVED_IF = {
    NOT_FOUND: "a scoped metadata check returns PRESENT for '{s}' and "
               "the re-extracted constraint is satisfied",
    CONFLICTING: "one authoritative version is confirmed and re-observed",
    INACCESSIBLE: "read access is granted and the content is re-observed",
    UNKNOWN: "a clearer source is observed and the requirement is "
             "re-extracted",
}
WHY = {
    NOT_FOUND: "blocks the verdict (documentary blocker)",
    CONFLICTING: "blocks the verdict (sources disagree)",
    INACCESSIBLE: "prevents a decision (evidence unread)",
    UNKNOWN: "prevents a decision (evidence gap)",
}
RESIDUAL = ("Whether the full project can actually be reconstructed — "
            "only a real restoration test proves that.")


def _pri(e):
    return 1 if e["status"] in (NOT_FOUND, CONFLICTING) else 2


def gen_planner(res):
    """A: why + cite + resolved-if + residual per action."""
    ev = sorted([e for e in res["evidence"] if e["status"] in ACTIONABLE],
                key=_pri)
    lines = [f"- P{_pri(e)}: {ACTION[e['status']].format(s=redact(e['subject']))} "
             f"(why: {WHY[e['status']]}; evidence: {e['source']}:{e['line']}; "
             f"resolved-if: {RESOLVED_IF[e['status']].format(s=redact(e['subject']))}; "
             f"authorization: no Skill write needed)"
             for e in ev]
    notes = [f"- Regardless of results: {RESIDUAL}"]
    return lines, notes


def gen_ledger(res):
    """B: every UNKNOWN/blocker carries an unknown-until expiry."""
    ev = sorted([e for e in res["evidence"] if e["status"] in ACTIONABLE],
                key=_pri)
    lines = [f"- P{_pri(e)}: '{redact(e['subject'])}' is {e['status']} "
             f"({e['source']}:{e['line']}); unknown-until: "
             f"{RESOLVED_IF[e['status']].format(s=redact(e['subject']))}; "
             f"action: {ACTION[e['status']].format(s=redact(e['subject']))}"
             for e in ev]
    return lines, []


def gen_counterfactual(res):
    """C: minimal evidence flips that could move the verdict."""
    ev = [e for e in res["evidence"] if e["status"] in ACTIONABLE]
    blockers = [e for e in ev if e["status"] in (NOT_FOUND, CONFLICTING)]
    lines = []
    for e in sorted(ev, key=_pri):
        if e["status"] in (NOT_FOUND, CONFLICTING):
            direction = ("toward clear" if len(blockers) == 1
                         else "toward fewer blockers")
        else:
            direction = "toward a decidable verdict"
        lines.append(
            f"- If '{redact(e['subject'])}' were resolved "
            f"({RESOLVED_IF[e['status']].format(s=redact(e['subject']))}; "
            f"evidence: {e['source']}:{e['line']}), the verdict could move "
            f"{direction}; check: "
            f"{ACTION[e['status']].format(s=redact(e['subject']))}")
    return lines, []


def gen_rootgroup(res):
    """D: downstream items grouped under their requiring document."""
    ev = [e for e in res["evidence"] if e["status"] in ACTIONABLE]
    groups = {}
    for e in ev:
        groups.setdefault(e["source"], []).append(e)
    lines = []
    for src in sorted(groups):
        items = sorted(groups[src], key=_pri)
        subs = ", ".join(f"'{redact(e['subject'])}' ({e['status']})"
                         for e in items)
        first = items[0]
        lines.append(
            f"- Root: {src} ({len(items)} item(s)): {subs}; first check: "
            f"{ACTION[first['status']].format(s=redact(first['subject']))} "
            f"(evidence: {first['source']}:{first['line']})")
    return lines, []


VARIANTS = {"A-planner": (gen_planner, "resolved-if:"),
            "B-ledger": (gen_ledger, "unknown-until:"),
            "C-counterfactual": (gen_counterfactual, "could move"),
            "D-rootgroup": (gen_rootgroup, "Root:")}


def score(variant, res):
    gen, marker = VARIANTS[variant]
    lines, notes = gen(res)
    subjects = {e["subject"] for e in res["evidence"]}
    cites = {f"{e['source']}:{e['line']}" for e in res["evidence"]}
    actionable = [e for e in res["evidence"]
                  if e["status"] in ACTIONABLE]
    covered = sum(1 for e in actionable
                  if any(redact(e["subject"]) in ln for ln in lines))
    grounded = sum(1 for ln in lines
                   if any(c in ln for c in cites)
                   and any(redact(s) in ln for s in subjects))
    criterion = sum(1 for ln in lines if marker in ln)
    size = sum(len(ln) for ln in lines + notes)
    return {"n_actionable": len(actionable), "lines": len(lines),
            "covered": covered,
            "grounded": grounded, "criterion": criterion, "size": size}


def main():
    print("variant | corpus | actionable | lines | covered | grounded "
          "| criterion | bytes")
    totals = {v: {"a": 0, "l": 0, "c": 0, "g": 0, "k": 0, "s": 0}
              for v in VARIANTS}
    for corpus in CORPORA:
        res = harness.run(HERE / "corpus" / corpus)
        for variant in VARIANTS:
            m = score(variant, res)
            t = totals[variant]
            t["a"] += m["n_actionable"]
            t["l"] += m["lines"]
            t["c"] += m["covered"]
            t["g"] += m["grounded"]
            t["k"] += m["criterion"]
            t["s"] += m["size"]
            print(f"{variant} | {corpus} | {m['n_actionable']} | "
                  f"{m['lines']} | {m['covered']} | {m['grounded']} | "
                  f"{m['criterion']} | {m['size']}")
    print("\nTOTALS variant | actionable | lines | covered | grounded "
          "| criterion | bytes")
    for variant, t in totals.items():
        print(f"{variant} | {t['a']} | {t['l']} | {t['c']} | {t['g']} | "
              f"{t['k']} | {t['s']}")


if __name__ == "__main__":
    main()
