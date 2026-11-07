# User-study protocol (no participants yet — do not invent outcomes)

Goal: measure whether PHOENIX helps a user find, understand, and resolve
a documentary blocker faster and more reliably than manual review.

## Design (within-subjects, counterbalanced)

- N target: 8–12 participants, mixed beginner/expert, none involved in
  building PHOENIX. Informed consent required; no personal files used.
- Each participant does 2 matched tasks: one with manual folder review,
  one with a PHOENIX first-run report + one recheck. Order randomized.
- Fixtures: closure-demo scenarios A (missing) and B (conflict),
  rebuilt in temp dirs so the "fix" step is real file work.

## Tasks (from system directive Objective 5)

1. T1: identify the real documentary blocker (which item?).
2. T2: count incorrect assumptions made before answering (think-aloud).
3. T3: locate the supporting evidence (file + line).
4. T4: state the next action in own words (graded against rubric).
5. T5: after applying the fix, determine resolved vs still-uncertain.

## Rubric (per task, 0/1/2)

- 2: correct + cited evidence. 1: correct, no citation. 0: wrong.
- T2 scored by count of false statements retracted or uncorrected.
- Time per task recorded with a stopwatch (start = fixture shown).

## Data template (one row per participant × task)

`pid, expertise(beginner|expert), condition(manual|phoenix), task,
score(0|1|2), seconds, notes`

## Analysis plan (descriptive only at N ≤ 12)

Report medians + ranges per condition; no p-values, no generalization
beyond the sample. Publish the raw table with the report.

## Status

NOT RUN. No participants recruited, no data collected. Running requires
human authorization (recruitment + consent) — recorded as pending.
