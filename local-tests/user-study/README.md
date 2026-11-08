# User-study task package (Delta) — ready to run, NOT RUN

No participants recruited, no data collected. This package plus
`../user-study-protocol.md` is everything a facilitator needs.

## Contents

- `fixtures.py` — builds task dirs (broken corpus + fix sheet for the
  facilitator + PHOENIX before-report printout).
- `results_template.csv` — one row per participant × task.
- `analyze.py` — medians + ranges per condition (descriptive only).
- `instructions.md` — facilitator script + participant brief + consent.

## Reproducibility

1. `python local-tests/user-study/fixtures.py A /tmp/study/A` (and `B`).
2. Print `TASK.md` (participant) and keep `FIX_SHEET.md`
   (facilitator-only) sealed until T5.
3. Follow `instructions.md` stopwatch procedure; record rows in a copy
   of `results_template.csv`.
4. `python local-tests/user-study/analyze.py results.csv` prints the
   summary. Publish the raw table with any report.

## Synthetic comprehension proxy (NOT a user study)

`python local-tests/user-study/comprehension_proxy.py` checks
deterministic readability properties of the §8 plain-language
sentences and §7 planner lines (sentence length, jargon scan,
required safety elements). It measures text properties, not human
understanding — the real study stays NOT RUN until humans participate.
