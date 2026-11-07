# Predicted report W1-D (core-d)

Local-harness prediction for same-day comparison with the real NAS report. A mismatch is a finding, not a failure.

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
- config/missing.yaml: NOT FOUND IN SCOPE — Bounded scope search returned no confirmed 'config/missing.yaml'. This is not proof of global absence. impact: presence cannot be confirmed; recovery must not assume it.
- runtime: CONFLICTING — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0. impact: no single observed version satisfies the requirement.

## 6. Contradictions
- runtime — Observed config/app.yaml:2 (2.9.0) contradicts required >= 3.0.

## 7. Next steps
- P1: Ask the operator to supply 'config/missing.yaml' or point to its approved location. (evidence: docs/deployment-guide.md:5; authorization: no Skill write needed)
- P1: Confirm the intended 'runtime' version with the document owners. (evidence: docs/deployment-guide.md:6 vs observed facts (see §4); authorization: no Skill write needed)

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
In plain terms: at least one required item is contradicted or cannot be confirmed from the reviewed sources — do not assume the project is recoverable.
Document-level assessment only — not a verified restore.
