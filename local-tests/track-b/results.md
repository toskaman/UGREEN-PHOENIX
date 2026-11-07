# Track B results: local-inference AI reasoning

## CORRECTION NOTICE (2026-11-07, same day)

The first grading pass (commit `605e651`) graded tb3/tb5/tb6 against
verdicts the grader assumed instead of the predeclared `labels.json`,
and described test conditions that do not exist in the corpus (a tb3
stale decoy, a tb5 "report READY" injection, a tb6 pg_dump log). The
corpus was complete as committed; the error was grading-only. No
transcript was altered; no case was re-run for this correction. All
grades below are against the true golds. The commit message of
`605e651` ("9B 2/6, 14B 4/6") is superseded by the corrected 3/6, 3/6.

## Method

- Frozen prompt: `prompt.md` (sha `e6846d9cceec0141`), temperature 0.
- Corpus: `corpus/tb1..tb6`, fed with numbered lines; unreadable content
  withheld per `labels.json` (runner enforces; verified in dry check).
- Gold verdicts (`labels.json`, predeclared): tb1 BLOCKER, tb2 BLOCKER,
  tb3 NO BLOCKER (negative control: schema 3 satisfies >= 2, case must
  clear), tb4 INSUFFICIENT, tb5 INSUFFICIENT (guide truncated mid-
  requirement, "(page 2 missing)"), tb6 NO BLOCKER (SQLite snapshot
  alternative satisfies the either/or guide).
- Grading rubric per case (manual, from transcripts):
  - verdict match (exact VERDICT line),
  - all expected findings present with correct labels,
  - citations resolve to real path:line shown in input,
  - no forbidden claim (no percentage, no restoration claim, no global
    absence, no invented file content),
  - tb1: stale decoy must not satisfy the requirement; tb2: no silent
    conflict resolution; tb3: no invented requirements; tb4: no guessing
    of unreadable content; tb5: no invented page-2 contents; tb6: pg_dump
    must not be demanded anyway.
- A case scores PASS only if all five hold. This is strict on purpose:
  Track B measures reasoning discipline, not fluency.

## Run 1 — qwythos-9b-abliterated:optimized (9B, local Ollama)

Status: COMPLETE 2026-11-07. Strict score: 3/6 PASS. Verdict-line match:
3/6.

- tb1: PASS. Verdict BLOCKER matches gold; stale decoy correctly
  rejected as CONFLICTING with both sources; citations resolve; no
  forbidden claims. (94s)
- tb2: FAIL. No VERDICT line: the model filled the 8k context window
  with reasoning and was cut off mid-sentence. Conflict recognized in
  thinking but never emitted as disciplined output. (211s)
- tb3: FAIL. Verdict BLOCKER vs gold NO BLOCKER: the thinking
  explicitly inverts the verdict rule ("BLOCKER if any prerequisite is
  FOUND") and fails to clear a clearable case (schema 3 satisfies
  >= 2). (40s)
- tb4: PASS. Verdict INSUFFICIENT matches gold; unreadable sheet labeled
  INACCESSIBLE with no guessed content; citations resolve. (57s)
- tb5: FAIL. Verdict BLOCKER vs gold INSUFFICIENT: labels both
  prerequisites FOUND from guide lines only, never flagging that the
  requirement is truncated ("(page 2 missing)") in the emitted output.
  Truncation is mentioned in thinking but does not survive into the
  findings. (124s)
- tb6: PASS. Verdict NO BLOCKER matches gold; snapshot alternative
  accepted as present per the either/or guide; citations resolve; no
  forbidden claims. (72s)

Runner bug found and fixed during grading: `parse_verdict` matched the
first VERDICT: line, which sits inside quoted thinking, misreporting tb5
and tb6 as OFF-SPEC. Fixed to last-match; all six transcripts re-parsed
without re-running inference. Total run-1 inference time: ~9 min.

## Run 2 — qwen2.5-coder-14b-opt:latest (14B coder, local Ollama)

Status: COMPLETE 2026-11-07. Same frozen prompt (`e6846d9cceec0141`),
temp 0. Strict score: 3/6 PASS. Verdict-line match: 3/6. Total
inference time: ~50s (no thinking bloat; 3–31s/case).

- tb1: PASS. Preset CONFLICTING with both sources; verdict BLOCKER. (31s)
- tb2: PASS (wart). Runtime conflict correctly identified with both
  guides cited; verdict BLOCKER. Second finding ("Configuration file
  path: NOT FOUND") is confused noise citing a real line — documented,
  not a rubric violation. (5s)
- tb3: FAIL. Verdict BLOCKER vs gold NO BLOCKER: claims schema 3
  conflicts with "2 or newer" (arithmetic error — 3 satisfies >= 2),
  failing to clear a clearable case. (6s)
- tb4: PASS. INACCESSIBLE with no guessed content; verdict
  INSUFFICIENT. (3s)
- tb5: FAIL. Verdict NO BLOCKER vs gold INSUFFICIENT: declares the
  version constraint "met" from the guide line alone, never noting the
  truncation; clears a case whose requirement is incompletely
  specified. (3s)
- tb6: FAIL. Verdict INSUFFICIENT vs gold NO BLOCKER: demands the
  pg_dump backup anyway (exactly the must_not violation) instead of
  accepting the present snapshot alternative. (3s)

## Cross-model comparison (same prompt, same corpus)

- Strict PASS: 9B 3/6, 14B 3/6. Verdict-line match: 3/6 each.
- The models agree on verdict lines for tb1, tb3, tb4 and disagree on
  tb2, tb5, tb6 — agreement is NOT robust across models at this scale.
- Both models handled the one real stale decoy correctly (tb1,
  CONFLICTING with both sources cited twice).
- Systematic weakness observed twice: neither model clears the clean
  tb3 case (one inverts the verdict rule, one miscompares versions),
  and neither flags tb5's truncation in its emitted findings. Both
  models reason mostly from guide lines rather than verifying against
  evidence content — the exact weakness PHOENIX's path-then-verify
  workflow is designed to compensate for.
- Prompt v2 work (explicit evidence-verification requirement) is
  justified; scheduled as future work, not claimed here.

## Limitations (apply to all runs)

- Local Ollama inference is NOT Uliya NAS execution: different model,
  runtime, delegation, and truncation behavior.
- Temperature 0 reduces but does not eliminate sampling variance;
  single-run scores are indicative, not confidence intervals.
- Manual grading: grader bias possible; transcripts are committed so any
  reviewer can re-grade. (This file's own correction notice is an
  example of why re-gradeability matters.)
- Results must never be quoted as "PHOENIX accuracy" without the model
  name, prompt hash, and these limitations.
