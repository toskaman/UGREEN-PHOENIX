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


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ver_key(version: str):
    return tuple(int(p) if p.isdigit() else p for p in version.split("."))


def compare(op: str, actual: str, wanted: str) -> bool:
    a, w = ver_key(actual), ver_key(wanted)
    return {"==": a == w, ">=": a >= w, "<=": a <= w,
            ">": a > w, "<": a < w}[op]


def run(scope: Path) -> dict:
    scope = scope.resolve()
    manifest = scope / "access-denied.txt"
    denied = set()
    if manifest.exists():
        denied = {l.strip().replace("\\", "/") for l in
                  manifest.read_text(encoding="utf-8").splitlines()
                  if l.strip()}

    # Step 1 — discovery (simulates file-agent find/ls/stat/sha256sum).
    discovered, inaccessible_files, skipped = [], [], []
    for path in sorted(scope.rglob("*")):
        if path.is_dir() or path.name == "access-denied.txt":
            continue
        rel = path.relative_to(scope).as_posix()
        if rel in denied:
            inaccessible_files.append(rel)  # never opened, never read
            continue
        if path.suffix.lower() in PARSED_SUFFIXES:
            discovered.append({"path": rel, "size": path.stat().st_size,
                               "sha256": sha256_of(path)})
        else:
            skipped.append(rel)

    # Step 2 — extraction (simulates document-agent qa/extract/reconcile).
    requirements, provisions, truncated_docs = [], [], []
    for entry in discovered:
        text = (scope / entry["path"]).read_text(encoding="utf-8",
                                                 errors="replace")
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
    for req in requirements:
        subj = req["subject"]
        if req["truncated_source"]:
            evidence.append({**req, "status": UNKNOWN,
                             "detail": "Source document is truncated; "
                                       "requirement cannot be confirmed."})
            continue
        if "/" in subj or "." in subj:  # file reference
            norm = subj.replace("\\", "/").lstrip("./")
            if norm in denied or subj in denied:
                evidence.append({**req, "status": INACCESSIBLE,
                                 "detail": f"'{subj}' cannot be read "
                                           f"(access denied)."})
            elif (scope / norm).exists():
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
                evidence.append({**req, "status": CONFLICTING,
                                 "detail": f"Observed {sources} contradicts "
                                           f"required {req['op']} "
                                           f"{req['version']}."})
            else:
                evidence.append({**req, "status": FOUND,
                                 "detail": f"Version fact satisfies "
                                           f"requirement."})

    # Step 4 — report assembly (simulates knowledge-agent collect-evidence).
    statuses = {e["status"] for e in evidence}
    if statuses & {NOT_FOUND, CONFLICTING}:
        verdict = "DOCUMENTARY BLOCKER IDENTIFIED"
    elif statuses & {INACCESSIBLE, UNKNOWN} or inaccessible_files:
        verdict = "INSUFFICIENT EVIDENCE"
    else:
        verdict = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"

    next_steps = []
    for e in evidence:
        if e["status"] == NOT_FOUND:
            next_steps.append(f"Ask the operator to supply '{e['subject']}' "
                              f"or point to its approved location.")
        elif e["status"] == CONFLICTING:
            next_steps.append(f"Confirm the intended '{e['subject']}' "
                              f"version with the document owners.")
        elif e["status"] in (INACCESSIBLE, UNKNOWN):
            next_steps.append(f"Resolve the '{e['subject']}' evidence gap "
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
             f"{len(inaccessible_files)}, truncated: {len(truncated_docs)}."]
    if inaccessible_files:
        lines.append("Inaccessible sources (content never read): "
                     + ", ".join(inaccessible_files))
    lines += ["", "## 3. Requirements"]
    lines += [f"- {e['subject']} (required by {e['source']}:{e['line']})"
              for e in evidence] or ["- none extracted"]
    lines += ["", "## 4. Evidence table"]
    for e in evidence:
        lines.append(f"- {e['subject']}: {e['status']} "
                     f"(required by {e['source']}:{e['line']}) — {e['detail']}")
    lines += ["", "## 5. Priority blockers"]
    lines += [f"- {e['subject']}: {e['status']} — {e['detail']}"
              for e in blockers] or ["- none"]
    lines += ["", "## 6. Contradictions and alternatives"]
    lines += [f"- {e['subject']} — {e['detail']}"
              for e in conflicts] or ["- none observed"]
    lines += ["", "## 7. Next verification actions"]
    lines += [f"- {s}" for s in next_steps] or ["- none"]
    lines += ["", f"## 8. Verdict: {verdict}",
              "Document-level assessment only — not a verified restore."]

    return {"verdict": verdict, "evidence": evidence,
            "coverage": {"reviewed": [d["path"] for d in discovered],
                         "skipped": skipped,
                         "inaccessible": inaccessible_files,
                         "truncated": truncated_docs},
            "report": "\n".join(lines)}


if __name__ == "__main__":
    result = run(Path(sys.argv[1]))
    print(result["report"])
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2),
                                     encoding="utf-8")
