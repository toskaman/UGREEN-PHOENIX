# v9 Beta — Evidence Gain Planner: selection, ablation, transfer

## 1. Candidate selection (deterministic, 8 frozen corpora)

`local-tests/ai-lab/experiments/beta_compare.py`. 12 actionable items
total. All variants reach full coverage/groundedness by construction;
discriminators are information content, size, and safety:

| variant | covered | grounded | criterion | bytes | verdict |
|---|---|---|---|---|---|
| A planner (why + resolved-if + residual) | 12/12 | 12/12 | 12/12 | 4256 | SHIP |
| B ledger (unknown-until only) | 12/12 | 12/12 | 12/12 | 2668 | folded into A (B ⊂ A) |
| C counterfactual ("could move…") | 12/12 | 12/12 | 12/12 | 3116 | REJECTED: verdict-direction heuristic is speculative |
| D root-group (group by guide) | 12/12 | 7 lines | 7 | 1464 | REJECTED: per-item cites diluted; same-guide ≠ same root cause |

## 2. Ablation v8 (HEAD code) vs v9 (Beta code), `/tmp/beta_ablate.py`

Real v8 `harness.py` from git HEAD vs worktree, same 8 corpora:

| metric | v8 | v9 |
|---|---|---|
| verdicts identical | 8/8 (baseline) | 8/8 |
| actions | 12 | 12 |
| actions with resolved-if | 0/12 | 12/12 |
| FIRST CHECK marked (non-empty §7) | 0/7 | 7/7 |
| Regardless-of-results residual | 0/7 | 7/7 |
| action cites valid | 12/12 | 12/12 |
| §7 bytes total | 1881 | 4448 |

Verdict logic untouched (asserted identical); the gain is purely
actionability at +2.5 KB across 8 reports.

## 3. Model transfer trial (14B + 9B, local Ollama, $0)

Scripts: `beta_planner_trial.py` (round 1, 8 calls),
`beta_planner_trial2.py` (round 2 guarded, 4 calls),
`beta_planner_trial3.py` (round 3 multi-item, 2 calls). Transcripts:
`ai-lab/reports/beta-trial*.txt`.

- Round 1: 4/8 strict. Genuine findings: 14B over-generated (4 lines
  for 1 item, incl. an invented alternative); 14B proposed a version
  UPDATE; 9B proposed similar-name search. The open action field
  invites drift. One FAIL was a scorer artifact (basename vs path).
- Round 2 (cardinality guard + verification-only allowlist): count
  and drift fixed 4/4, but [FIRST CHECK]/residual markers dropped
  (instruction load vs cosmetic markers). 0/4 strict, 4/4 near-pass.
- Round 3 (2-item, post-think scorer): 9B strict PASS; 14B placed
  FIRST CHECK correctly and stayed verification-only but degraded
  cites to non-path:line labels and dropped the residual dash.

Transfer verdict: the planner CORE (one line per item, why,
resolved-if, verification-only, exact cites) transfers; COSMETIC
markers ([FIRST CHECK] brackets, residual dash) are flaky on proxy
models, and 14B trades citation discipline for constraint juggling
under long instructions. Native instruction must stay short with
citation discipline first (see Zeta).

## 4. Ship decision: SHIP WITH GUARDS

Shipped: `harness.py` §7 (1:1 by construction, verification-only
templates), `decision-protocol.md` item 7/9 (cardinality guard +
verification-only allowlist), `SKILL.md` step-5 in-context guard
("exactly one Next-steps action per evidence row; verification
checks only, no invented actions"), acceptance check `planner: FIRST
CHECK + why + resolved-if + residual` (92/92).

Watch items for finalist day: 14B twice phrased verification as
"any other directory" (scope-drift wording; step-4 Category rules
still bind); residual dash dropped 3/3 by 14B (substance kept).
