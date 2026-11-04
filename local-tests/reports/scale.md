# PHOENIX local simulation report

## 1. Scenario
Scope: scale (local synthetic corpus, NOT a NAS runtime result).

## 2. Coverage
Documents reviewed: 42, skipped non-documents: 1, inaccessible: 0, truncated: 0.

## 3. Requirements
- app/main.py (required by docs/guide.md:4)
- config/app.yaml (required by docs/guide.md:5)
- config/missing.yaml (required by docs/guide.md:6)
- runtime (required by docs/guide.md:7)
- worker (required by docs/guide.md:8)

## 4. Evidence table
- app/main.py: FOUND (required by docs/guide.md:4) — 'app/main.py' verified present in scope.
- config/app.yaml: FOUND (required by docs/guide.md:5) — 'config/app.yaml' verified present in scope.
- config/missing.yaml: NOT FOUND IN SCOPE (required by docs/guide.md:6) — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.
- runtime: FOUND (required by docs/guide.md:7) — Version fact satisfies requirement.
- worker: UNKNOWN (required by docs/guide.md:8) — No observed version fact for 'worker'.

## 5. Priority blockers
- config/missing.yaml: NOT FOUND IN SCOPE — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence.

## 6. Contradictions and alternatives
- none observed

## 7. Next verification actions
- Ask the operator to supply 'config/missing.yaml' or point to its approved location.
- Resolve the 'worker' evidence gap (access or clearer source needed).

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
Document-level assessment only — not a verified restore.
