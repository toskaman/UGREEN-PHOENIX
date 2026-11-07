# PHOENIX local simulation report

## 1. Scenario
Scope: edge-2 (local synthetic corpus, NOT a NAS runtime result).

## 2. Coverage
Documents reviewed: 3, skipped non-documents: 0, inaccessible: 0, truncated: 0.
Completion: COMPLETED.

## 3. Requirements
- runtime (required by docs/guide-v1.md:4)
- runtime (required by docs/guide-v2.md:4)

## 4. Evidence table
- runtime: CONFLICTING (required by docs/guide-v1.md:4) — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.
- runtime: FOUND (required by docs/guide-v2.md:4) — Version fact satisfies requirement.

## 5. Priority blockers
- runtime: CONFLICTING — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## 6. Contradictions
- runtime — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## 7. Next steps
- Confirm the intended 'runtime' version with the document owners.

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
In plain terms: at least one required item is contradicted or cannot be confirmed from the reviewed sources — do not assume the project is recoverable.
Document-level assessment only — not a verified restore.
