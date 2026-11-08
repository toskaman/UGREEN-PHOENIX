# Predicted report W1-B (core-b)

Local-harness prediction for same-day comparison with the real NAS report. A mismatch is a finding, not a failure.

# PHOENIX local simulation report

## 1. Scenario
Scope: core-b (local synthetic corpus, NOT a NAS runtime result).

## 2. Coverage
Documents reviewed: 3, skipped non-documents: 0, inaccessible: 0, truncated: 0.
Completion: COMPLETED.

## 3. Requirements
- config/runtime.yaml (required by docs/deployment-guide.md:4)
- runtime (required by docs/deployment-guide.md:5)

## 4. Evidence table
- config/runtime.yaml: FOUND (required by docs/deployment-guide.md:4) — 'config/runtime.yaml' verified present in scope.
- runtime: CONFLICTING (required by docs/deployment-guide.md:5) — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## 5. Priority blockers
- runtime: CONFLICTING — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0. impact: no single observed version satisfies the requirement.

## 6. Contradictions
- runtime — Observed config/runtime.yaml:2 (2.4.1) contradicts required >= 3.0.

## 7. Next steps
- P1: [FIRST CHECK] Confirm the intended 'runtime' version with the document owners. (why: blocks the verdict (sources disagree); evidence: docs/deployment-guide.md:5 vs observed facts (see §4); resolved-if: one authoritative version is confirmed and re-observed; authorization: no Skill write needed)
- Regardless of results: whether the full project can actually be reconstructed stays unverified — only a real restoration test proves that.

## 8. Verdict: DOCUMENTARY BLOCKER IDENTIFIED
In plain terms: at least one required item is contradicted or cannot be confirmed from the reviewed sources — do not assume the project is recoverable.
Document-level assessment only — not a verified restore.
