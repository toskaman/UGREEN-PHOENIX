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

import harness

BLOCKER = "DOCUMENTARY BLOCKER IDENTIFIED"
CLEAR = "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES"
ABSTAIN = "INSUFFICIENT EVIDENCE"

REQUIRES_RE = re.compile(r"^REQUIRES:\s*(\S+)(?:\s*(==|>=|<=|>|<)\s*(\S+))?\s*$")
PROVIDES_RE = re.compile(r"^PROVIDES:\s*(\S+)\s+(\S+)\s*$")
DOC_SUFFIXES = {".md", ".yaml", ".yml", ".txt"}


def _documents(scope: Path) -> dict:
    docs = {}
    for path in sorted(scope.rglob("*", recurse_symlinks=False)):
        if (path.is_file() and not path.is_symlink()
                and path.suffix.lower() in DOC_SUFFIXES
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
    basenames = {p.name for p in scope.rglob("*", recurse_symlinks=False)
                 if p.is_file() and not p.is_symlink()}
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


def _rich_requirements(docs: dict) -> list:
    reqs = []
    for rel, text in docs.items():
        for lineno, line in enumerate(text.splitlines(), 1):
            m = REQUIRES_RE.match(line.strip())
            if m:
                reqs.append((m.group(1), m.group(2), m.group(3),
                             f"{rel}:{lineno}"))
    return reqs


def _provides(docs: dict) -> dict:
    facts = {}
    for text in docs.values():
        for line in text.splitlines():
            m = PROVIDES_RE.match(line.strip())
            if m and m.group(1) not in facts:
                facts[m.group(1)] = m.group(2)
    return facts


def retrieval_plus(scope: Path) -> dict:
    """Exact-path retrieval plus version analysis, with citations.

    Well-designed retrieval (exact scoped paths, real version comparison,
    source:line citations) that abstains only when a named version has no
    observed fact. It still has no evidence labels, no access-denied or
    truncated-source handling, and no unsafe-path discipline: whatever is
    readable on disk counts as evidence.
    """
    scope = scope.resolve()
    docs = _documents(scope)
    facts = _provides(docs)
    rows = []
    for subject, op, version, source in _rich_requirements(docs):
        if _is_file_subject(subject):
            target = harness.safe_join(scope, subject)
            status = ("MISSING" if target is None or not target.exists()
                      else "FOUND")
        elif op and subject in facts:
            status = ("FOUND" if harness.compare(op, facts[subject], version)
                      else "MISSING")
        else:
            status = "UNFOUNDED"  # named version with no observed fact
        rows.append({"subject": subject, "status": status, "source": source})
    if any(r["status"] == "MISSING" for r in rows):
        verdict = BLOCKER
    elif any(r["status"] == "UNFOUNDED" for r in rows):
        verdict = ABSTAIN
    else:
        verdict = CLEAR
    return {"verdict": verdict, "rows": rows, "cited": True}
