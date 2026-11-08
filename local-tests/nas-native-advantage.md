# NAS-native advantage (Phase Gamma) — falsifiable comparison

Question: **"Why can't a normal document chatbot do the same thing
just as well?"**

Short answer: a chatbot given pasted text can match words, but it
cannot verify existence inside an authorized scope, reconcile
conflicting version claims against observed files, handle denied or
truncated sources, or re-observe after a fix. Each missing capability
produces a measured false clear or wrong verdict below. All numbers
are local simulation (`run-baseline.py`, 8 cases × 3 runs), not NAS
runtime evidence.

## Capability ladder (same 8 frozen cases)

| # | configuration | measured as | verdicts | false clears |
|---|---|---|---|---|
| 1 | pasted-text chatbot (substring match, no cites) | `generic_qa` | 1/8 | 5 |
| 2 | filename retrieval (basename match, versions assumed) | `filename_search` | 3/8 | 3 |
| 3 | exact paths + versions, no conflict reconciliation | `phoenix_no_reconcile` | 6/8 | 0 (misses 2 blockers as INSUFFICIENT) |
| 4 | full PHOENIX (verify + reconcile + abstain) | `phoenix` | 8/8 | 0 |
| 5 | PHOENIX + Recovery Closure (re-observe after fix) | `render-demo` A/B/C | 3/3 deltas correct | 0 |

Strong cited retrieval (`retrieval_plus`, exact paths + versions +
cites) reaches 6/8 but scores 0/2 abstention: it clears `edge`
(truncated/hostile) and over-blocks `edge-3` (denied reference)
instead of abstaining.

## Decisive cases (per-case table, `baseline-comparison.md:39-59`)

- `core-a` (missing config, decoy present): chatbot and filename
  search CLEAR — the decoy filename looks healthy. PHOENIX verifies
  the exact path and reports the blocker. Falsifier: exact-path
  verification.
- `edge` (truncated/hostile source): ALL naive methods CLEAR;
  PHOENIX abstains (INSUFFICIENT EVIDENCE). A chatbot cannot tell
  "unreadable" from "healthy" without extraction metadata.
- `edge-3` (access-denied reference): chatbot CLEARs (misses);
  retrieval_plus BLOCKERs (wrong — denied is not disproven);
  PHOENIX abstains. Falsifier: permission-aware access handling.
- `core-b` / `edge-2` (version conflict): without reconciliation
  the verdict collapses to INSUFFICIENT (2 missed blockers).
  Falsifier: cross-document reconcile + observed-file arbitration.
- Closure (config 5): after the operator supplies the file, PHOENIX
  re-observes and emits RESOLVED (A/B) or STILL UNCERTAIN (C, decoy
  fix). A chatbot has no re-observation step — "I fixed it" is
  unverifiable. Falsifier: Recovery Delta on fresh evidence.

## What the NAS provides that pasted text cannot

1. Authorized scope with exact paths (`ug-filesystem` find/stat) —
   decoys fail, traversal fails, absence is bounded not global.
2. Observed file bytes vs documented claims (`ug-document`
   extract/reconcile) — conflicts arbitrated, not averaged.
3. Access-denied and truncated signals as first-class evidence —
   abstention instead of false clears.
4. Re-inspection after a real file change (Recovery Closure) —
   before/after Delta on fresh evidence.
5. Citation traceability: 22/22 rows cited vs 0/22 for naive
  methods — every claim re-checkable by the user.

No claim is made about speed, privacy, or on-device inference
residency: none is measured. The advantage is evidential, and each
link above names the case that would falsify it.
