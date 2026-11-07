# Assistant vs PHOENIX: what changes with Recovery Closure

Honest comparison of three ways to answer "is my project archive ready
for reconstruction?" All three read the same authorized folder. The
difference is workflow, evidence discipline, and what happens after the
first answer.

## 1. Ordinary AI document assistant (chatbot + pasted text)

- Input: whatever text the user chose to copy. No file existence check,
  no paths, no metadata, no hashes, no notion of scope.
- Output: a fluent summary. May silently pick one side of a conflict,
  treat a same-named file as the required one, or treat "I fixed it" as
  proof. No output contract; format varies per run.
- After the fix: user pastes new text and asks again. No comparison with
  the prior answer; regressions and new gaps are invisible unless the
  user spots them.
- Failure mode: confident prose with no auditable link between claim and
  source. Track B tb2/tb5/tb6 show models defaulting to forced verdicts
  or hallucinated detail when the prompt does not forbid it.

## 2. Document QA that produces only a report (PHOENIX pre-v4)

- Input: authorized scope via file-agent/document-agent; exact paths,
  sizes, line citations, scope ban on traversal and global claims.
- Output: fixed 8-section report + conservative verdict ordering
  (BLOCKER > CONFLICT > INSUFFICIENT > READY-ish). Deterministic and
  reproducible where the platform allows.
- After the fix: a fresh report. Better evidence, but still no link
  between the two reports: the user must diff prose by hand to know
  whether the blocker is really resolved.
- Failure mode: correct single-shot analysis that leaves the user alone
  at the hardest step — "did my fix actually work?"

## 3. PHOENIX with Recovery Closure (v4)

Adds, on top of (2), with no new APIs:

- DISCOVER/EXPLAIN: every finding carries subject, label, reason, and a
  path:line citation the user can open themselves.
- RECOMMEND: prioritized P1 (blockers) before P2 (gaps); each action
  names its evidence and its authorization requirement; restore-family
  verbs are banned from recommendations so the Skill never promises a
  restoration it cannot perform.
- RECHECK: re-inspection uses newly observed evidence only. The prior
  report is never reused as evidence — it is only compared against.
- COMPARE: a Recovery Delta section with per-finding states (RESOLVED /
  STILL BLOCKED / NEW BLOCKER / STILL UNCERTAIN / NEW GAP / UNCHANGED /
  NEW / REMOVED), new evidence cited, unknowns named, next action given.
  Works even without platform persistence: the prior report is supplied
  by the user or retrieved as an ordinary document.

## Workflow difference in one table

| Step | Chatbot | Report-only QA | PHOENIX Closure |
|---|---|---|---|
| Verify the file exists at the documented path | no | yes | yes |
| Cite path:line for every claim | sometimes | yes | yes |
| Refuse global absence claims | no | yes | yes |
| Prioritized fix instructions | generic | no | yes (P1/P2) |
| Re-inspect with fresh evidence | no | manual re-run | yes, enforced |
| Before/after delta with states | no | no | yes |
| Claim restoration without a test | often implied | no | explicitly refused |

## Why the NAS matters here (supported capabilities only)

A chatbot with pasted text cannot: confirm a file exists at a path, see
exact paths/sizes/hashes, reconcile two documents it was never shown
together, or re-read a folder after a fix. PHOENIX Closure turns those
platform capabilities into a loop — check, fix, recheck, compare — that
is meaningless without tool access to the stored files. That loop, not
any single answer, is the NAS-native advantage.

Validated by: `run-tests.py` closure A/B/C checks (scenarios A/B/C in
`closure-demo.md`), mutation set (delta mutants), and Track B cases
tb1–tb6 with transcripts under `track-b/transcripts/`.
