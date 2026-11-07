# v5 failure analysis (interim, Cycle 2 — local models, $0 spend)

Gold source: `track-b/labels.json` (v4, predeclared). Prompt v1 = frozen
v4 prompt; v2/v3 = `ai-lab/prompts/`. Strict rubric = v4 results.md.

## TB2 — context exhaustion (9B)

- v1: NO-VERDICT after 211s (8k window filled with deliberation).
- v2: NO-VERDICT after 192s (same mechanism).
- Root cause (confirmed from transcripts): the 9B thinking model echoes
  input files and deliberates unboundedly, ignoring "output ONLY"
  instructions. The LONGER v2 prompt made it worse: v2 tb1 also burned
  (206s, 31K chars, no FINDINGS) where v1 tb1 succeeded in 94s.
- Conclusion: prompt wording cannot fix TB2 on small thinking models.
  Fixes must be structural: provider-side reasoning budgets (Vultr
  `reasoning.max_tokens`, staged), non-thinking models, or prompt depth
  matched to model capacity (Arch F). TB2 = model/capacity limitation,
  honestly bounded, not prompt-fixed.

## TB3 — version comparison (both models failed v1)

- 9B v1: inverted the verdict rule. 14B v1: claimed 3 conflicts with ≥2.
- v2 adds an explicit numeric comparison procedure ("3 >= 2" worked
  example + write-the-comparison requirement).
- 14B v2 tb3: PASS — "declares portal schema 3, which satisfies
  '2 or newer' (3 >= 2)", verdict NO BLOCKER. TB3 FIXED on 14B.
- 9B v2 tb3: PASS — findings cite evidence files, schema 3 accepted,
  verdict NO BLOCKER. TB3 FIXED on 9B too.
- Conclusion: mechanical procedures stated in-prompt DO transfer across
  both local models. This is the strongest v5 reasoning improvement.

## TB5 — truncation handling (both models failed v1)

- v1: 9B forced BLOCKER, 14B cleared (NO BLOCKER); neither flagged the
  "(page 2 missing)" truncation in emitted findings.
- v2 adds a truncation rule (truncated-only requirements are UNKNOWN;
  name what is missing).
- 14B v2 tb5: PASS — "UNKNOWN — Page 2 is missing, truncating the
  requirement", verdict INSUFFICIENT. TB5 FIXED on 14B.
- 9B v2 tb5: pending (run in progress).
- Side effect (14B v2 tb6): a confused extra finding ("Truncation note
  missing" on a non-truncated case) — rule leakage, verdict still
  correct. Recorded as wart; shows rules can over-fire.

## TB6 — alternative dependencies (14B failed v1)

- v1: 14B demanded pg_dump anyway (must_not violation), verdict
  INSUFFICIENT vs gold NO BLOCKER. 9B v1 passed.
- v2 adds an alternative rule (ONE satisfied OR-branch is enough).
- 14B v2 tb6: PASS (wart above) — snapshot accepted, verdict NO
  BLOCKER. TB6 FIXED on 14B.
- 9B v2 tb6: pending.

## tb1 regression under v2 (14B)

- v1: CONFLICTING correctly (PASS). v2: INACCESSIBLE, verdict
  INSUFFICIENT (FAIL), stable across 2 runs — systematic, not noise.
- Hypothesis: added rules shifted classification of the stale-decoy
  situation. Fix attempt: v3 adds a superseded-file rule (stale-marked
  files never satisfy; cite both sources as CONFLICTING). v3 tb1 test
  pending (waiting for GPU: 9B run in progress).
- Net v2 on 14B: 3/6 → 5/6 strict (tb1 the only fail). Arch C gate
  agrees 5/6: all citations resolve, zero forbidden claims.

## Scoreboard (strict)

| Config | tb1 | tb2 | tb3 | tb4 | tb5 | tb6 | Total |
|---|---|---|---|---|---|---|---|
| 9B v1 | P | F | F | P | F | P | 3/6 |
| 14B v1 | P | P | F | P | F | F | 3/6 |
| 14B v2 | F | P | P | P | P | P* | 5/6 |
| 9B v2 | F | F | P | ? | ? | ? | ≥1/6 |

P* = pass with documented wart. ?: 9B run in progress.

## Arch B pipeline (Cycle 3) — final 14B results

Single-shot prompting hit rule-interference (v2 fixed tb3, broke tb1;
v3 fixed tb1, broke tb3; two single-variable hypotheses refuted), so
judgment moved to deterministic code per the architecture pivot:

- b1c extraction + aggregate + verify + file-anchored escalation.
- Track B: 6/6. Dev x01–x10: 10/10. Validation x11–x20: 10/10.
- Pipeline total 26/26 (verified fresh; includes x10 injection
  resisted — extraction has no verdict to hijack).
- Deterministic nets added from live failures: UNREADABLE correction
  vs withheld map, fail-closed empty extraction, same-file conflict
  scope, observed-value disagreement, truncation net (fires on exactly
  tb5/x09/x27/x28, zero false positives over 36 cases), ALT grounding
  (±2-line either/or window), bare-version equality, ALT option-path
  matching, tab/pipe rows, wrapped-row joining, chatter rejection.
- 9B transfer: 5/6 Track B (up from 3/6 v1 and 2/6 v2), zero context
  burns. Residual: tb6 extraction recall (snapshot row missed) —
  small-model recall is the remaining risk; unseen-file escalation
  recorded as future work, not implemented.
