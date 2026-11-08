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
- runtime: FOUND (required by docs/guide-v2.md:4) — Version fact satisfies requirement (observed config/runtime.yaml:2 (2.4.1)).

## 5. Priority blockers
- runtime: CONFLICTING — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0. impact: no single observed version satisfies the requirement.

## 6. Contradictions
- runtime — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## 7. Next steps
- P1: [FIRST CHECK] Confirm the intended 'runtime' version with the document owners. (why: blocks the verdict (sources disagree); evidence: docs/guide-v1.md:4 vs observed facts (see §4); resolved-if: one authoritative version is confirmed and re-observed; authorization: no Skill write needed)
- Regardless of results: whether the full project can actually be reconstructed stays unverified — only a real restoration test proves that.

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
In plain terms: at least one required item is contradicted or cannot be confirmed from the reviewed sources — do not assume the project is recoverable.
Document-level assessment only — not a verified restore.
