"""Deterministic Recovery Delta: prior state + current findings -> state.

Inputs: prior verdict + prior blocker (subject/path, from the supplied
prior report or test labels), and the CURRENT aggregated findings.
The prior report is NEVER reused as evidence; it only names what to
look up in current findings. No model calls.
"""

STATES = ("RESOLVED", "STILL BLOCKED", "STILL UNCERTAIN", "NEW BLOCKER",
          "NEW GAP", "UNCHANGED")

GENERIC = {"file", "files", "config", "folder", "document", "required",
           "the", "a"}


def _match(prior_subject: str, finding_subject: str) -> bool:
    pa = {w for w in prior_subject.lower().split()
          if len(w) >= 3 and w not in GENERIC}
    fa = {w for w in finding_subject.lower().split()
          if len(w) >= 3 and w not in GENERIC}
    return bool(pa & fa)


def compute(prior_verdict: str, prior_blockers: list,
            current: dict) -> dict:
    """prior_blockers: [{subject, path}]. current: aggregate() output."""
    deltas = []
    for pb in prior_blockers:
        cands = [f_ for f_ in current["findings"]
                 if _match(pb["subject"], f_["subject"])]
        if not cands:
            # subject vanished from findings: blocker gone only if the
            # file now verifies elsewhere; conservative: UNCERTAIN unless
            # current verdict is fully clear with no unknowns.
            if current["verdict"] == \
                    "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES":
                deltas.append({"prior": pb["subject"], "state": "RESOLVED",
                               "why": "no current finding contests it"})
            else:
                deltas.append({"prior": pb["subject"],
                               "state": "STILL UNCERTAIN",
                               "why": "subject absent from current findings"})
            continue
        labels = {c["label"] for c in cands}
        if labels <= {"FOUND"}:
            deltas.append({"prior": pb["subject"], "state": "RESOLVED",
                           "why": "observed in current files"})
        elif labels & {"CONFLICTING", "NOT FOUND IN SCOPE"}:
            deltas.append({"prior": pb["subject"], "state": "STILL BLOCKED",
                           "why": "current findings still adverse"})
        else:
            deltas.append({"prior": pb["subject"], "state": "STILL UNCERTAIN",
                           "why": "current evidence inconclusive"})
    return {"deltas": deltas, "current_verdict": current["verdict"]}
