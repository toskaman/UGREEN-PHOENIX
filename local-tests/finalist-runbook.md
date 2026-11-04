# Finalist 24-hour NAS runbook (PHOENIX)

Goal: spend the remote session on real NAS execution, not preparation.
Everything below assumes the local work in this repo is already green.

## Before the session

- [ ] Skill package ready: `SKILL.md` + `references/` in a directory named
      `phoenix-recovery-intelligence` (checker `static-pass` re-verified).
- [ ] All 7 corpora from `local-tests/corpus/` zipped for upload.
- [ ] `labels.json` printed: expected verdict per corpus.
- [ ] Answers to `open-questions-for-ugreen.md` received and applied.
- [ ] Screen recording tested; demo script rehearsed (see below).
- [ ] Clock plan shared with the team; roles assigned (driver + notetaker).

## Hour 0–2 — access and smoke test

1. Confirm access method, skill install procedure, and observable logs.
2. Record platform versions (kit, capability catalog, and which model
   actually runs the Skill — press reports a 4B-class on-device model with
   cloud APIs possible; confirm fixed-label compliance on the observed
   model before trusting verdicts).
3. Install the Skill; run one minimal prompt on `core-c` (expect no
   blocker). If install fails, escalate immediately — do not burn hours.

## Hour 2–10 — core evidence runs

Run each corpus with its scenario prompt; save every report verbatim:

| Order | Corpus | Must observe |
|---|---|---|
| 1 | core-c | No blocker, all cited |
| 2 | core-a | Blocker on `config/prod-config.yaml`, decoy rejected |
| 3 | core-b | `CONFLICTING` with both sources cited |
| 4 | core-d | Mixed table, exact labels |
| 5 | edge | `INSUFFICIENT EVIDENCE`, no leak, injection ignored |
| 6 | edge-2 | Disagreement surfaced as `CONFLICTING` |
| 7 | scale | Coverage counts, timing |

For each run capture: prompt, full report, expert delegation trace if
visible, timestamps, and any approval dialogs (screenshot).

## Hour 10–16 — iterate and re-verify

- Fix Skill wording for every deviation from `labels.json`.
- Re-run the static checker after each edit (stay at zero diagnostics).
- Re-run affected corpora; record before/after reports.

## Hour 16–20 — demo video

Suggested 3-minute outline (adapt to final rules):

1. (0:00–0:30) Problem: files present, recoverability unknown.
2. (0:30–1:30) Live run on `core-a`: missing config found, decoy rejected,
   cited report shown.
3. (1:30–2:15) Live run on `core-b`: version conflict with both sources.
4. (2:15–2:45) Honesty statement: documentary readiness, not a verified
   restore; edge-case abstention clip.
5. (2:45–3:00) Closing: what was tested on the real NAS.

Record narration separately if live audio is risky; keep raw footage.

## Hour 20–24 — package and buffer

- [ ] Freeze the final Skill package; final checker run.
- [ ] Export all evidence: reports, logs, screenshots, video files.
- [ ] Draft the Devpost final update (results, limits, video link).
- [ ] Unused hours are buffer — do not start new features.

## Evidence checklist (must leave the session with)

- Platform version record, 7+ NAS reports, delegation/approval captures,
  timing notes, demo video + raw footage, final package with checker output.
