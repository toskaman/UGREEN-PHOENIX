# Recovery Readiness Passport (design, v5)

A portable, evidence-backed report that travels with a project and
documents its recovery readiness at a point in time. It is the PHOENIX
report plus identity, history, and limits — still plain text, still
produced only from authorized-scope evidence, still approval-gated when
saved to the NAS.

## Sections

1. Identity: project name, scope path, scenario, date, PHOENIX version.
2. Verdict: one of the three standard verdicts, in plain language.
3. Requirements: the Proof Graph (nodes + edges + citations).
4. Evidence limits: coverage, inaccessible sources, truncation notes,
   model/uncertainty disclaimer.
5. Blockers: prioritized P1/P2 with evidence and next actions.
6. Resolution history: Recovery Deltas from prior passports for the
   same scope (each stamped with its own date; prior passports are
   compared, never trusted).
7. Next checks: what would invalidate this passport (new files,
   version changes, moved folders).

## Anti-guarantee (printed on every passport)

> This passport documents EVIDENCE REVIEWED, not a tested recovery.
> It expires the moment the scope changes. Only a real restoration
> test proves recoverability.

## Why it matters commercially

- Studios can attach a passport to project handovers and audits.
- IT can show prerequisite review happened (compliance trail).
- UGREEN can render passport history as a UGOS dashboard later
  (Enterprise feature, not the hackathon Skill).

## Out of scope for the Skill

Machine-readable signatures, cross-NAS verification, scheduled
re-issue. Those need platform APIs that do not exist today.
