"""PHOENIX local workflow-logic harness.

Simulates the PHOENIX decision procedure (discover -> extract -> verify ->
report) against a synthetic local corpus. This validates the workflow LOGIC
only: it is NOT a NAS runtime test and proves nothing about Uliya experts,
NAS permissions, or model quality on a real device.

Marker spec (parsed from .md/.yaml/.txt documents, never from free text):
  REQUIRES: <path-or-name> [==|>=|<=|>|< <version>]
  PROVIDES: <name> <version>
  EXTRACTION TRUNCATED            -> marks the whole document as partial
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

MAX_VERSION_LENGTH = 64
MAX_VERSION_SEGMENTS = 16
MAX_DEPTH = 12
SECRET_RE = re.compile(r"(?i)\b(password|passwd|secret|api[\s_-]?key|"
                       r"access[\s_-]?token|private[\s_-]?key|"
                       r"client[\s_-]?secret|connection[\s_-]?string|"
                       r"bearer)\s*[:=]\s*\S+")
TOKEN_RE = re.compile(r"\b(ghp_[A-Za-z0-9_]+|gho_[A-Za-z0-9_]+|"
                      r"xox[bpars]-[A-Za-z0-9-]+|sk-[A-Za-z0-9]{8,})\b")


def redact(text: str) -> str:
    """Mask obvious secret assignments and well-known token prefixes."""
    def _mask(match):
        head = re.sub(r"\s*[:=]\s*\S+$", "", match.group(0))
        return head + "=[REDACTED]"
    masked = SECRET_RE.sub(_mask, text)
    return TOKEN_RE.sub("[REDACTED-TOKEN]", masked)


def norm_rel(entry: str):
    """Normalize a manifest/relative path; return None if it escapes."""
    parts = [q for q in entry.strip().replace("\\", "/").split("/")
             if q not in ("", ".")]
    if not parts or any(q == ".." for q in parts):
        return None
    return "/".join(parts)


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


def run(scope: Path, mode: str = "full") -> dict:
    """Run the decision procedure. mode='full', or ablation 'no_reconcile'
    (contradictions degrade to UNKNOWN) or 'no_verify' (basename match)."""
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
        truncated = TRUNCATED_MARKER in text
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
            m = PROVIDES_RE.match(line)
            if m:
                name, version = m.groups()
                provisions.append({"name": name, "version": version,
                                   "source": entry["path"], "line": lineno})

    # Step 3 — verification (simulates targeted file-agent checks).
    evidence = []
    all_basenames = {p.name for p in scope.rglob("*", recurse_symlinks=False)
                     if p.is_file() and not p.is_symlink()}
    for req in requirements:
        subj = req["subject"]
        if req["truncated_source"]:
            evidence.append({**req, "status": UNKNOWN,
                             "detail": "Source document is truncated; "
                                       "requirement cannot be confirmed."})
            continue
        if "/" in subj or "." in subj:  # file reference
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
                evidence.append({**req, "status": FOUND,
                                 "detail": f"Version fact satisfies "
                                           f"requirement."})

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

    next_steps = []
    for e in evidence:
        subject = redact(e["subject"])
        if e["status"] == NOT_FOUND:
            next_steps.append(f"Ask the operator to supply '{subject}' "
                              f"or point to its approved location.")
        elif e["status"] == CONFLICTING:
            next_steps.append(f"Confirm the intended '{subject}' "
                              f"version with the document owners.")
        elif e["status"] in (INACCESSIBLE, UNKNOWN):
            next_steps.append(f"Resolve the '{subject}' evidence gap "
                              f"(access or clearer source needed).")

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
              f"{redact(e['detail'])}"
              for e in blockers] or ["- none"]
    lines += ["", "## 6. Contradictions"]
    lines += [f"- {redact(e['subject'])} — {redact(e['detail'])}"
              for e in conflicts] or ["- none observed"]
    lines += ["", "## 7. Next steps"]
    lines += [f"- {s}" for s in next_steps] or ["- none"]
    lines += ["", f"## 8. Verdict: {verdict}",
              f"In plain terms: {PLAIN_VERDICT[verdict]}",
              "Document-level assessment only — not a verified restore."]

    return {"verdict": verdict, "completion": completion,
            "evidence": evidence,
            "coverage": {"reviewed": [d["path"] for d in discovered],
                         "skipped": skipped,
                         "inaccessible": inaccessible_files,
                         "truncated": truncated_docs,
                         "symlinks_skipped": symlinks,
                         "errors": discovery_errors,
                         "depth_capped": depth_capped},
            "report": "\n".join(lines)}


if __name__ == "__main__":
    result = run(Path(sys.argv[1]))
    print(result["report"])
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2),
                                     encoding="utf-8")
