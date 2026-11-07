# PHOENIX local simulation report

## 1. Scenario
Scope: core-d (local synthetic corpus, NOT a NAS runtime result).

## 2. Coverage
Documents reviewed: 2, skipped non-documents: 1, inaccessible: 0, truncated: 0.
Completion: COMPLETED.

## 3. Requirements
- app/main.py (required by docs/deployment-guide.md:4)
- config/missing.yaml (required by docs/deployment-guide.md:5)
- runtime (required by docs/deployment-guide.md:6)

## 4. Evidence table
- app/main.py: FOUND (required by docs/deployment-guide.md:4) — 'app/main.py' verified present in scope.
- config/missing.yaml: NOT FOUND IN SCOPE (required by docs/deployment-guide.md:5) — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.
- runtime: CONFLICTING (required by docs/deployment-guide.md:6) — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0.

## 5. Priority blockers
- config/missing.yaml: NOT FOUND IN SCOPE — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.
- runtime: CONFLICTING — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0.

## 6. Contradictions
- runtime — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0.

## 7. Next steps
- Ask the operator to supply 'config/missing.yaml' or point to its approved location.
- Confirm the intended 'runtime' version with the document owners.

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
In plain terms: at least one required item is contradicted or cannot be confirmed from the reviewed sources — do not assume the project is recoverable.
Document-level assessment only — not a verified restore.
