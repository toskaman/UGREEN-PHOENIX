"""PHOENIX local workflow-logic harness.

Simulates the PHOENIX decision procedure (discover -> extract -> verify ->
report) against a synthetic local corpus. This validates the workflow LOGIC
only: it is NOT a NAS runtime test and proves nothing about Uliya experts,
NAS permissions, or model quality on a real device.

Marker spec (parsed from .md/.yaml/.txt documents, never from free text):
  REQUIRES: <path-or-name> [==|>=|<=|>|< <version> | <version> or newer]
  PROVIDES: <name> <version>
  EXTRACTION TRUNCATED            -> alone on its own line, marks the whole
                                     document as partial
  access-denied.txt (manifest)    -> listed paths are INACCESSIBLE, never read

Scope safety (all enforced, all tested):
  symlinks are never followed; traversal/absolute subjects are rejected as
  UNKNOWN and never resolved outside the scope; manifest entries are
  normalized before comparison; version strings are compared with a total
  ordering that cannot raise and cannot confuse two distinct long versions;
  OS read errors map to never-used INACCESSIBLE entries instead of crashing;
  directory trees deeper than MAX_DEPTH are capped and reported.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

REQUIRES_RE = re.compile(r"^REQUIRES:\s*(\S+)(?:\s*(==|>=|<=|>|<)\s*(\S+))?\s*$")
REQUIRES_OR_NEWER_RE = re.compile(
    r"^REQUIRES:\s*(\S+)\s+(\S+)\s+or\s+(newer|later)\s*$", re.IGNORECASE)
PROVIDES_RE = re.compile(r"^PROVIDES:\s*(\S+)\s+(\S+)\s*$")
TRUNCATED_MARKER = "EXTRACTION TRUNCATED"
PARSED_SUFFIXES = {".md", ".yaml", ".yml", ".txt"}

FOUND = "FOUND"
CONFLICTING = "CONFLICTING"
NOT_FOUND = "NOT FOUND IN SCOPE"
INACCESSIBLE = "INACCESSIBLE"
UNKNOWN = "UNKNOWN"

COMPLETED = "COMPLETED"
PARTIAL = "PARTIAL"

PLAIN_VERDICT = {
    "DOCUMENTARY BLOCKER IDENTIFIED":
        "at least one required item is contradicted or cannot be confirmed "
        "from the reviewed sources — do not assume the project is recoverable.",
    "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES":
        "every extracted requirement was confirmed in the reviewed sources — "
        "this is still not a tested restore.",
    "INSUFFICIENT EVIDENCE":
        "some evidence could not be read or confirmed, so no conclusion is "
        "possible yet.",
}

BLOCKER_STATES = {NOT_FOUND, CONFLICTING}
GAP_STATES = {INACCESSIBLE, UNKNOWN}

IMPACT = {
    NOT_FOUND: "presence cannot be confirmed; recovery must not assume it.",
    CONFLICTING: "no single observed version satisfies the requirement.",
}


def violates_restore_ban(text: str) -> bool:
    """True when a recommendation claims restore-like action."""
    return re.search(r"\b(restore\w*|recover\w*|rebuild\w*)\b",
                     text, re.IGNORECASE) is not None

MAX_VERSION_LENGTH = 64
MAX_VERSION_SEGMENTS = 16
MAX_DEPTH = 12
SECRET_RE = re.compile(r"(?i)\b(password|passwd|secret|api[\s_-]?key|"
                       r"access[\s_-]?token|private[\s_-]?key|"
                       r"client[\s_-]?secret|connection[\s_-]?string|"
                       r"bearer)\s*(?:[:=]|\bis\b)\s*\S+")
BEARER_RE = re.compile(r"(?i)\bBearer\s+\S+")
PEM_RE = re.compile(r"-----BEGIN [^-]*PRIVATE KEY[^-]*-----"
                    r".*?-----END [^-]*PRIVATE KEY[^-]*-----", re.DOTALL)
PEM_MARKER_RE = re.compile(r"-----[A-Z ]*PRIVATE KEY[^-]*-----")
TOKEN_RE = re.compile(r"\b(ghp_[A-Za-z0-9_]+|gho_[A-Za-z0-9_]+|"
                      r"xox[bpars]-[A-Za-z0-9-]+|sk-[A-Za-z0-9]{8,}|"
                      r"AKIA[0-9A-Z]{16}|"
                      r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b")


def redact(text: str) -> str:
    """Mask obvious secret assignments and well-known token prefixes."""
    def _mask(match):
        head = re.sub(r"(?:\s*[:=]\s*|\s+is\s+)\S+$", "", match.group(0),
                      flags=re.IGNORECASE)
        return head + "=[REDACTED]"
    masked = SECRET_RE.sub(_mask, text)
    masked = BEARER_RE.sub("Bearer [REDACTED]", masked)
    masked = PEM_RE.sub("[REDACTED-PEM]", masked)
    masked = PEM_MARKER_RE.sub("[REDACTED-PEM]", masked)
    return TOKEN_RE.sub("[REDACTED-TOKEN]", masked)


def norm_rel(entry: str):
    """Normalize a manifest/relative path; return None if it escapes.

    Comparison form is lowercased: norm_rel feeds deny-list checks only
    (never display or resolution), so case variants of a denied path on
    case-insensitive filesystems still match the manifest.
    """
    parts = [q for q in entry.strip().replace("\\", "/").split("/")
             if q not in ("", ".")]
    if not parts or any(q == ".." for q in parts):
        return None
    return "/".join(parts).lower()


def safe_join(scope: Path, user_path: str):
    """Resolve user_path inside scope; return None if unsafe/out-of-scope."""
    text = user_path.replace("\\", "/")
    if not text or text.startswith("/") or re.match(r"^[A-Za-z]:", text):
        return None
    candidate = (scope / text).resolve()
    try:
        candidate.relative_to(scope)
    except ValueError:
        return None
    return candidate


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_probe(path: Path):
    """Return (size, sha256), or None when the OS refuses access."""
    try:
        return path.stat().st_size, sha256_of(path)
    except OSError:
        return None


def _safe_read(path: Path):
    """Return file text, or None when the OS refuses access."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def ver_key(version: str):
    key = []
    for part in version[:MAX_VERSION_LENGTH].split(".")[:MAX_VERSION_SEGMENTS]:
        key.append((0, int(part)) if part.isdigit() else (1, part[:32]))
    key.append((2, len(version),
                hashlib.sha256(version.encode("utf-8",
                                              errors="replace")).hexdigest()))
    return tuple(key)


def compare(op: str, actual: str, wanted: str) -> bool:
    a, w = ver_key(actual), ver_key(wanted)
    return {"==": a == w, ">=": a >= w, "<=": a <= w,
            ">": a > w, "<": a < w}[op]


KNOWN_VERDICTS = frozenset(PLAIN_VERDICT)
KNOWN_STATES = frozenset({FOUND, CONFLICTING, NOT_FOUND, INACCESSIBLE,
                          UNKNOWN})


def _sanitize_prior(prior, scope_name):
    """Validate a user-supplied prior report for delta comparison.

    Returns (verdict, prev_map) of validated data, or (None, None) when
    the prior is malformed or bound to a different scope: the delta is
    then withheld instead of echoing untrusted content.
    """
    if not isinstance(prior, dict):
        return None, None
    verdict = prior.get("verdict")
    if verdict not in KNOWN_VERDICTS:
        return None, None
    if prior.get("scope") != scope_name:
        return None, None
    raw = prior.get("evidence")
    if not isinstance(raw, list):
        return None, None
    prev_map = {}
    for entry in raw:
        if not isinstance(entry, dict):
            return None, None
        subject = entry.get("subject")
        status = entry.get("status")
        detail = entry.get("detail")
        if not isinstance(subject, str) or not subject:
            return None, None
        if status not in KNOWN_STATES:
            return None, None
        if not isinstance(detail, str):
            return None, None
        prev_map[subject] = {"status": status, "detail": detail}
    return verdict, prev_map


def run(scope: Path, mode: str = "full", prior: dict | None = None) -> dict:
    """Run the decision procedure. mode='full', or ablation 'no_reconcile'
    (contradictions degrade to UNKNOWN) or 'no_verify' (basename match).
    prior is a previous result dict used ONLY for delta comparison; all
    evidence is re-observed from the scope on every run."""
    scope = scope.resolve()
    manifest = scope / "access-denied.txt"
    denied = set()
    if manifest.exists():
        denied = {n for n in
                  (norm_rel(line) for line in manifest.read_text(
                      encoding="utf-8", errors="replace").splitlines())
                  if n}

    # Step 1 — discovery (simulates file-agent find/ls/stat/sha256sum).
    discovered, inaccessible_files, skipped, symlinks = [], [], [], []
    discovery_errors, depth_capped = [], 0
    for path in sorted(scope.rglob("*", recurse_symlinks=False)):
        if path.is_dir() or path.name == "access-denied.txt":
            continue
        rel = path.relative_to(scope).as_posix()
        if len(path.relative_to(scope).parts) > MAX_DEPTH:
            depth_capped += 1
            continue
        if path.is_symlink():
            symlinks.append(rel)
            continue  # never followed, never opened
        if norm_rel(rel) in denied:
            inaccessible_files.append(rel)  # never opened, never read
            continue
        if path.suffix.lower() in PARSED_SUFFIXES:
            probed = _safe_probe(path)
            if probed is None:
                discovery_errors.append(rel + " (unreadable)")
                continue
            size, digest = probed
            discovered.append({"path": rel, "size": size, "sha256": digest})
        else:
            skipped.append(rel)

    # Step 2 — extraction (simulates document-agent qa/extract/reconcile).
    requirements, provisions, truncated_docs = [], [], []
    for entry in discovered:
        text = _safe_read(scope / entry["path"])
        if text is None:
            discovery_errors.append(entry["path"] + " (unreadable)")
            continue
        truncated = any(line.strip() == TRUNCATED_MARKER
                        for line in text.splitlines())
        if truncated:
            truncated_docs.append(entry["path"])
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            m = REQUIRES_RE.match(line)
            if m:
                subject, op, version = m.groups()
                requirements.append({"subject": subject, "op": op,
                                     "version": version,
                                     "source": entry["path"], "line": lineno,
                                     "truncated_source": truncated})
                continue
            m = REQUIRES_OR_NEWER_RE.match(line)
            if m:
                requirements.append({"subject": m.group(1), "op": ">=",
                                     "version": m.group(2),
                                     "source": entry["path"], "line": lineno,
                                     "truncated_source": truncated})
                continue
            m = PROVIDES_RE.match(line)
            if m:
                name, version = m.groups()
                provisions.append({"name": name, "version": version,
                                   "source": entry["path"], "line": lineno})
                continue
            if line.startswith("REQUIRES:"):
                requirements.append({
                    "subject": line.split(":", 1)[1].strip() or line,
                    "op": None, "version": None,
                    "source": entry["path"], "line": lineno,
                    "truncated_source": truncated, "unparsed": True})

    # Step 3 — verification (simulates targeted file-agent checks).
    evidence = []
    all_basenames = {p.name for p in scope.rglob("*", recurse_symlinks=False)
                     if p.is_file() and not p.is_symlink()}
    provision_names = {p["name"] for p in provisions}
    for req in requirements:
        subj = req["subject"]
        if req["truncated_source"]:
            evidence.append({**req, "status": UNKNOWN,
                             "detail": "Source document is truncated; "
                                       "requirement cannot be confirmed."})
            continue
        if req.get("unparsed"):
            evidence.append({**req, "status": UNKNOWN,
                             "detail": "Requirement line could not be "
                                       "parsed; no confirmation possible."})
            continue
        if "/" in subj or ("." in subj and req["op"] is None
                           and subj not in provision_names):  # file reference
            norm = norm_rel(subj)
            if norm is not None and norm in denied:
                evidence.append({**req, "status": INACCESSIBLE,
                                 "detail": f"'{subj}' cannot be read "
                                           f"(access denied)."})
                continue
            if mode == "no_verify":
                base = subj.replace("\\", "/").split("/")[-1]
                if base in all_basenames:
                    evidence.append({**req, "status": FOUND,
                                     "detail": f"Basename '{base}' matched "
                                               f"somewhere (no verification)."})
                else:
                    evidence.append({**req, "status": NOT_FOUND,
                                     "detail": f"No file named '{base}'."})
                continue
            target = safe_join(scope, subj)
            if target is None:
                evidence.append({**req, "status": UNKNOWN,
                                 "detail": f"'{subj}' is not a safe in-scope "
                                           f"path; rejected without resolving "
                                           f"outside the scope."})
            elif target.exists():
                # Aliased references only (symlinks, dot-segments): direct
                # references are owned by the name check above, so a
                # resolved target is re-checked only when aliasing made it
                # differ from the requested name.
                resolved = norm_rel(target.relative_to(scope).as_posix())
                if resolved != norm and resolved in denied:
                    evidence.append({**req, "status": INACCESSIBLE,
                                     "detail": f"'{subj}' cannot be read "
                                               f"(access denied)."})
                else:
                    evidence.append({**req, "status": FOUND,
                                     "detail": f"'{subj}' verified present in "
                                               f"scope."})
            else:
                evidence.append({**req, "status": NOT_FOUND,
                                 "detail": f"Bounded scope search returned "
                                           f"no confirmed '{subj}'. This is "
                                           f"not proof of global absence."})
        else:  # named capability with version constraint
            matches = [p for p in provisions if p["name"] == subj]
            if not matches:
                evidence.append({**req, "status": UNKNOWN,
                                 "detail": f"No observed version fact for "
                                           f"'{subj}'."})
            elif req["op"] and all(
                    not compare(req["op"], p["version"], req["version"])
                    for p in matches):
                sources = ", ".join(
                    f"{p['source']}:{p['line']} ({p['version']})"
                    for p in matches)
                if mode == "no_reconcile":
                    evidence.append({**req, "status": UNKNOWN,
                                     "detail": "Version comparison ran, but "
                                               "reconciliation is disabled "
                                               "in this ablation."})
                else:
                    evidence.append({**req, "status": CONFLICTING,
                                     "detail": f"Observed {sources} "
                                               f"contradicts required "
                                               f"{req['op']} {req['version']}."})
            else:
                satisfied = ", ".join(
                    f"{p['source']}:{p['line']} ({p['version']})"
                    for p in matches
                    if not req["op"] or compare(
                        req["op"], p["version"], req["version"]))
                evidence.append({**req, "status": FOUND,
                                 "detail": f"Version fact satisfies "
                                           f"requirement (observed "
                                           f"{satisfied})."})

    # Step 4 — report assembly (simulates knowledge-agent collect-evidence).
    statuses = {e["status"] for e in evidence}
    if statuses & {NOT_FOUND, CONFLICTING}:
        verdict = "DOCUMENTARY BLOCKER IDENTIFIED"
    elif (statuses & {INACCESSIBLE, UNKNOWN} or inaccessible_files
          or discovery_errors or depth_capped):
        verdict = "INSUFFICIENT EVIDENCE"
    else:
        verdict = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"

    if (inaccessible_files or truncated_docs or discovery_errors
            or depth_capped):
        completion = "PARTIAL"
    else:
        completion = "COMPLETED"

    # Recovery Closure: compare against the user-supplied prior report.
    # Prior data is NEVER reused as evidence; everything above was
    # re-observed from the scope on this run.
    delta = None
    if prior:
        prior_verdict, prev_map = _sanitize_prior(prior, scope.name)
    else:
        prior_verdict, prev_map = None, None
    if prev_map is not None:
        new_map = {e["subject"]: e["status"] for e in evidence}
        prev_status = {s: e["status"] for s, e in prev_map.items()}
        transitions = []
        for subject in sorted(set(prev_status) | set(new_map)):
            old, new = prev_status.get(subject), new_map.get(subject)
            if new == FOUND and old in (BLOCKER_STATES | GAP_STATES):
                # A cleared blocker AND a confirmed gap both resolve:
                # evidence now supports the subject. (Red-team v6:
                # gap->FOUND used to fall through to "REMOVED".)
                state = "RESOLVED"
            elif new in BLOCKER_STATES and old not in BLOCKER_STATES:
                state = "NEW BLOCKER"
            elif new in BLOCKER_STATES:
                state = "STILL BLOCKED"
            elif old in GAP_STATES and new in GAP_STATES:
                state = "STILL UNCERTAIN"
            elif new in GAP_STATES:
                state = "NEW GAP"
            elif old == new:
                state = "UNCHANGED"
            elif old is None:
                state = "NEW"
            elif new is None:
                state = "UNVERIFIED"
            else:
                state = "REMOVED"
            transitions.append({
                "subject": subject, "previous": old, "current": new,
                "state": state,
                "prior_detail": (redact(prev_map[subject]["detail"])
                                 if subject in prev_map else None),
                "new_detail": next((redact(e["detail"]) for e in evidence
                                    if e["subject"] == subject), None)})
        resolved = [t["subject"] for t in transitions
                    if t["state"] == "RESOLVED"]
        delta = {"prior_verdict": prior_verdict, "verdict": verdict,
                 "transitions": transitions, "resolved": resolved,
                 "resolved_count": len(resolved)}

    recommendations = []
    for e in evidence:
        subject = redact(e["subject"])
        source = f"{e['source']}:{e['line']}"
        if e["status"] == NOT_FOUND:
            recommendations.append({
                "subject": subject, "priority": 1,
                "action": f"Ask the operator to supply '{subject}' or "
                          f"point to its approved location.",
                "evidence": source, "auth": "no Skill write needed"})
        elif e["status"] == CONFLICTING:
            recommendations.append({
                "subject": subject, "priority": 1,
                "action": f"Confirm the intended '{subject}' version "
                          f"with the document owners.",
                "evidence": f"{source} vs observed facts (see §4)",
                "auth": "no Skill write needed"})
        elif e["status"] == INACCESSIBLE:
            recommendations.append({
                "subject": subject, "priority": 2,
                "action": f"Request read access to '{subject}' or an "
                          f"approved copy.",
                "evidence": source,
                "auth": "access grant is the operator's decision"})
        elif e["status"] == UNKNOWN:
            recommendations.append({
                "subject": subject, "priority": 2,
                "action": f"Resolve the '{subject}' evidence gap with a "
                          f"clearer source.",
                "evidence": source, "auth": "no Skill write needed"})
    recommendations.sort(key=lambda r: r["priority"])

    blockers = [e for e in evidence
                if e["status"] in (NOT_FOUND, CONFLICTING)]
    conflicts = [e for e in evidence if e["status"] == CONFLICTING]
    lines = ["# PHOENIX local simulation report", "",
             "## 1. Scenario",
             f"Scope: {scope.name} (local synthetic corpus, "
             "NOT a NAS runtime result).", "",
             "## 2. Coverage",
             f"Documents reviewed: {len(discovered)}, skipped "
             f"non-documents: {len(skipped)}, inaccessible: "
             f"{len(inaccessible_files)}, truncated: {len(truncated_docs)}.",
             f"Completion: {completion}."]
    if inaccessible_files:
        lines.append("Inaccessible sources (content never read): "
                     + ", ".join(inaccessible_files))
    if symlinks:
        lines.append("Symlinked entries skipped (never followed): "
                     + ", ".join(symlinks))
    if discovery_errors:
        lines.append("Unreadable files (OS error, content never used): "
                     + ", ".join(discovery_errors))
    if depth_capped:
        lines.append(f"Entries below depth {MAX_DEPTH} not reviewed: "
                     f"{depth_capped}.")
    lines += ["", "## 3. Requirements"]
    lines += [f"- {redact(e['subject'])} "
              f"(required by {e['source']}:{e['line']})"
              for e in evidence] or ["- none extracted"]
    lines += ["", "## 4. Evidence table"]
    for e in evidence:
        lines.append(f"- {redact(e['subject'])}: {e['status']} "
                     f"(required by {e['source']}:{e['line']}) — "
                     f"{redact(e['detail'])}")
    lines += ["", "## 5. Priority blockers"]
    lines += [f"- {redact(e['subject'])}: {e['status']} — "
              f"{redact(e['detail'])} impact: {IMPACT[e['status']]}"
              for e in blockers] or ["- none"]
    lines += ["", "## 6. Contradictions"]
    lines += [f"- {redact(e['subject'])} — {redact(e['detail'])}"
              for e in conflicts] or ["- none observed"]
    lines += ["", "## 7. Next steps"]
    lines += [f"- P{r['priority']}: {r['action']} (evidence: {r['evidence']}; "
              f"authorization: {r['auth']})"
              for r in recommendations] or ["- none"]
    lines += ["", f"## 8. Verdict: {verdict}",
              f"In plain terms: {PLAIN_VERDICT[verdict]}",
              "Document-level assessment only — not a verified restore."]
    if delta is not None:
        lines += ["", "## 9. Recovery Delta",
                  f"Verdict: {delta['prior_verdict']} -> {delta['verdict']}.",
                  f"Documentary blockers resolved: {delta['resolved_count']}. "
                  "This is not a tested restoration."]
        for tr in delta["transitions"]:
            lines.append(f"- {redact(tr['subject'])}: {tr['previous']} -> "
                         f"{tr['current']} — {tr['state']}")
        unknowns = [tr["subject"] for tr in delta["transitions"]
                    if tr["state"] in ("STILL UNCERTAIN", "NEW GAP")]
        if unknowns:
            lines.append("Still unknown: "
                         + ", ".join(redact(u) for u in unknowns) + ".")
        lines.append("Next action: address the remaining blockers or gaps "
                     "above, then run one more recheck with this report "
                     "as prior.")

    return {"verdict": verdict, "completion": completion, "scope": scope.name,
            "evidence": evidence, "recommendations": recommendations,
            "delta": delta,
            "coverage": {"reviewed": [d["path"] for d in discovered],
                         "skipped": skipped,
                         "inaccessible": inaccessible_files,
                         "truncated": truncated_docs,
                         "symlinks_skipped": symlinks,
                         "errors": discovery_errors,
                         "depth_capped": depth_capped},
            "report": "\n".join(lines)}


if __name__ == "__main__":
    prior = None
    if len(sys.argv) > 3:
        try:
            prior = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print("prior report unreadable; continuing without delta",
                  file=sys.stderr)
            prior = None
    result = run(Path(sys.argv[1]), prior=prior)
    print(result["report"])
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2),
                                     encoding="utf-8")
