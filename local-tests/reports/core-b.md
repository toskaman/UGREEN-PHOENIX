# PHOENIX local simulation report
Scope: core-b (local synthetic corpus, NOT a NAS runtime result)
Documents reviewed: 3, skipped non-documents: 0, inaccessible: 0, truncated: 0

## Evidence
- config/runtime.yaml: FOUND (required by docs/deployment-guide.md:4) — 'config/runtime.yaml' verified present in scope.
- runtime: CONFLICTING (required by docs/deployment-guide.md:5) — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## Next verification actions
- Confirm the intended 'runtime' version with the document owners.

## Verdict: DOCUMENTARY BLOCKER IDENTIFIED
Document-level assessment only — not a verified restore.
