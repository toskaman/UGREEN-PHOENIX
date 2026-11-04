# Predicted report W1-G (scale)

Local-harness prediction for same-day comparison with the real NAS report. A mismatch is a finding, not a failure.

# PHOENIX local simulation report
Scope: scale (local synthetic corpus, NOT a NAS runtime result)
Documents reviewed: 42, skipped non-documents: 1, inaccessible: 0, truncated: 0

## Evidence
- app/main.py: FOUND (required by docs/guide.md:4) — 'app/main.py' verified present in scope.
- config/app.yaml: FOUND (required by docs/guide.md:5) — 'config/app.yaml' verified present in scope.
- config/missing.yaml: NOT FOUND IN SCOPE (required by docs/guide.md:6) — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.
- runtime: FOUND (required by docs/guide.md:7) — Version fact satisfies requirement.
- worker: UNKNOWN (required by docs/guide.md:8) — No observed version fact for 'worker'.

## Next verification actions
- Ask the operator to supply 'config/missing.yaml' or point to its approved location.
- Resolve the 'worker' evidence gap (access or clearer source needed).

## Verdict: DOCUMENTARY BLOCKER IDENTIFIED
Document-level assessment only — not a verified restore.
