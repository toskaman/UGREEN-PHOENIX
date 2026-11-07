# PHOENIX local simulation report

## 1. Scenario
Scope: edge-3 (local synthetic corpus, NOT a NAS runtime result).

## 2. Coverage
Documents reviewed: 1, skipped non-documents: 1, inaccessible: 1, truncated: 0.
Inaccessible sources (content never read): docs/locked.md

## 3. Requirements
- docs/locked.md (required by docs/guide.md:4)
- ../escape.txt (required by docs/guide.md:5)
- C:/abs.txt (required by docs/guide.md:6)
- app/main.py (required by docs/guide.md:7)

## 4. Evidence table
- docs/locked.md: INACCESSIBLE (required by docs/guide.md:4) — 'docs/locked.md' cannot be read (access denied).
- ../escape.txt: UNKNOWN (required by docs/guide.md:5) — '../escape.txt' is not a safe in-scope path; rejected without resolving outside the scope.
- C:/abs.txt: UNKNOWN (required by docs/guide.md:6) — 'C:/abs.txt' is not a safe in-scope path; rejected without resolving outside the scope.
- app/main.py: FOUND (required by docs/guide.md:7) — 'app/main.py' verified present in scope.

## 5. Priority blockers
- none

## 6. Contradictions and alternatives
- none observed

## 7. Next verification actions
- Resolve the 'docs/locked.md' evidence gap (access or clearer source needed).
- Resolve the '../escape.txt' evidence gap (access or clearer source needed).
- Resolve the 'C:/abs.txt' evidence gap (access or clearer source needed).

## 8. Verdict: INSUFFICIENT EVIDENCE
Document-level assessment only — not a verified restore.
