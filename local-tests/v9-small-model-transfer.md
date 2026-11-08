# v9 Zeta — small-model robustness (`v9-small-model-transfer.md`)

Experiment: `ai-lab/experiments/zeta_compare.py` (8 calls) +
`zeta_verify.py` (1 call). Transcripts: `ai-lab/reports/zeta-*.txt`.
Task: assemble the report from fixed upstream results (core-a
BLOCKER, edge INSUFFICIENT). Full instruction 177 words, short 78.

## Result: 3/8 — short REJECTED, checklist SHIPPED

| model | case | full (177w) | short (78w) |
|---|---|---|---|
| 14B | core-a | PASS | FAIL: verdict "CONFLICTING" (label/verdict confusion) + action on a FOUND item |
| 14B | edge | FAIL: FALSE CLEAR on truncated case | FAIL: verdict "CONFLICTING" + fake cites ("cite: Discovery") |
| 9B | core-a | PASS (but "locate or create" drift — Zeta FULL lacked the verification-only clause) | FAIL: verdict "CONFLICTING" + 3 actions for 2 rows |
| 9B | edge | PASS | FAIL: verdict "CONFLICTING" + fake cites ("cite: Verification:5") |

Short-instruction failure is systematic (0/4): compression destroys
verdict semantics first. Per the exit condition, the shorter version
is REJECTED — no transfer regression will be shipped to save context.

## Shipped fix: in-context verdict checklist

14B false-cleared the truncated case even with the full rule stated.
A mechanical checklist ("worst label wins; a clear verdict next to
any UNKNOWN/INACCESSIBLE row is forbidden") fixed the cell
(`zeta_verify.py`: PASS, INSUFFICIENT EVIDENCE, 31s). The checklist
now lives in SKILL step-5 in-context (not only in the linked
protocol), pinned by contract check #20.

## Residual unknowns (reserved for NAS testing)

- Uliya's real instruction-following vs these proxies (9B/14B
  disagree with each other: 9B abstains, 14B clears without the
  checklist).
- Residual-line discipline: 14B emits "Regardless-of-results." stubs
  and dash-less residuals; substance usually kept, format flaky.
- Scope-drift wording ("any other directory", "production
  environment") appears under both instructions; step-4 Category
  rules still bind, but finalist day must watch the phrasing.
- Scorer leniency note: cites_ok passed when the true cite appeared
  anywhere in the body, even beside fake cites — the fake-cite
  finding above is manual transcript reading, not the scorer.
