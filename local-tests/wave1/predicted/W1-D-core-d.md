# Predicted report W1-D (core-d)

Local-harness prediction for same-day comparison with the real NAS report. A mismatch is a finding, not a failure.

# PHOENIX local simulation report
Scope: core-d (local synthetic corpus, NOT a NAS runtime result)
Documents reviewed: 2, skipped non-documents: 1, inaccessible: 0, truncated: 0

## Evidence
- app/main.py: FOUND (required by docs/deployment-guide.md:4) — 'app/main.py' verified present in scope.
- config/missing.yaml: NOT FOUND IN SCOPE (required by docs/deployment-guide.md:5) — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.
- runtime: CONFLICTING (required by docs/deployment-guide.md:6) — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0.

## Next verification actions
- Ask the operator to supply 'config/missing.yaml' or point to its approved location.
- Confirm the intended 'runtime' version with the document owners.

## Verdict: DOCUMENTARY BLOCKER IDENTIFIED
Document-level assessment only — not a verified restore.
