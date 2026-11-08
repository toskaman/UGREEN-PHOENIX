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


def _tokens(text: str) -> set[str]:
    return {w for w in text.lower().split()
            if len(w) >= 3 and w not in GENERIC}


def _path_hit(prior_path: str, finding: dict) -> bool:
    if not prior_path or prior_path == "-":
        return False
    if prior_path in (finding.get("req_path", ""),
                      finding.get("obs_path", "")):
        return True
    srcs = {s.split(":")[0].strip()
            for s in finding.get("sources", "").split(",") if s.strip()}
    return prior_path in srcs


def _match(prior: dict, finding: dict) -> bool:
    """Path-anchored match: the prior path must appear in the finding
    (required/observed path or sources), or subject tokens must overlap
    on at least TWO significant words. A single shared word ('token',
    'file') never resolves a blocker by itself."""
    if _path_hit(prior.get("path", ""), finding):
        return True
    overlap = _tokens(prior.get("subject", "")) & \
        _tokens(finding.get("subject", ""))
    return len(overlap) >= 2


def compute(prior_verdict: str, prior_blockers: list,
            current: dict) -> dict:
    """prior_blockers: [{subject, path}]. current: aggregate() output."""
    deltas = []
    for pb in prior_blockers:
        cands = [f_ for f_ in current["findings"]
                 if _match(pb, f_)]
        if not cands:
            # Subject vanished from findings. Absence of a finding is
            # never evidence of re-verification: a recheck that does
            # not mention the subject at all is a coverage gap, so the
            # state stays UNCERTAIN even when the rest reads clear.
            # (A genuine fix shows up as a matched FOUND row instead.)
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
