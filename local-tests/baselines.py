"""Naive comparison baselines.

filename_search: a REQUIRES file subject is FOUND when any file with the same
  basename exists anywhere in scope (content, location, and freshness are
  ignored); version requirements cannot be evaluated and are assumed
  satisfied. Never abstains, emits no source citations.
generic_qa: a REQUIRES subject is SATISFIED when its literal text appears
  anywhere in the corpus documents (a mere mention counts as evidence).
  Never abstains, emits no source citations.

Both baselines ignore the access-denied manifest (they have no access
concept), unlike PHOENIX, which never opens denied files.
"""

import re
from pathlib import Path

BLOCKER = "DOCUMENTARY BLOCKER IDENTIFIED"
CLEAR = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"

REQUIRES_RE = re.compile(r"^REQUIRES:\s*(\S+)(?:\s*(?:==|>=|<=|>|<)\s*\S+)?\s*$")
DOC_SUFFIXES = {".md", ".yaml", ".yml", ".txt"}


def _documents(scope: Path) -> dict:
    docs = {}
    for path in sorted(scope.rglob("*")):
        if (path.is_file() and path.suffix.lower() in DOC_SUFFIXES
                and path.name != "access-denied.txt"):
            docs[path.relative_to(scope).as_posix()] = path.read_text(
                encoding="utf-8", errors="replace")
    return docs


def _requirements(docs: dict) -> list:
    reqs = []
    for rel, text in docs.items():
        for line in text.splitlines():
            m = REQUIRES_RE.match(line.strip())
            if m:
                reqs.append(m.group(1))
    return reqs


def _is_file_subject(subject: str) -> bool:
    return "/" in subject or "." in subject


def filename_search(scope: Path) -> dict:
    scope = scope.resolve()
    basenames = {p.name for p in scope.rglob("*") if p.is_file()}
    rows = []
    for subject in _requirements(_documents(scope)):
        if _is_file_subject(subject):
            base = subject.replace("\\", "/").split("/")[-1]
            status = "FOUND" if base in basenames else "MISSING"
        else:
            status = "ASSUMED-SATISFIED"
        rows.append({"subject": subject, "status": status})
    verdict = BLOCKER if any(r["status"] == "MISSING" for r in rows) else CLEAR
    return {"verdict": verdict, "rows": rows, "cited": False}


def generic_qa(scope: Path) -> dict:
    scope = scope.resolve()
    docs = _documents(scope)
    blob = "\n".join(docs.values())
    rows = [{"subject": s,
             "status": "SATISFIED" if s in blob else "UNSATISFIED"}
            for s in _requirements(docs)]
    verdict = (BLOCKER if any(r["status"] == "UNSATISFIED" for r in rows)
               else CLEAR)
    return {"verdict": verdict, "rows": rows, "cited": False}
