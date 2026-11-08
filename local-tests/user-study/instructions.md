# Facilitator script + participant brief + consent

## Consent (read aloud, signed before starting)

"This is a usability test of a project-recovery assistant. You will
inspect two small synthetic project folders and answer questions. No
personal files are involved; everything is fictional test data. Your
answers and timings are recorded anonymously as a participant number.
You may stop at any time with no consequences. Do you consent to
participate?"

## Participant brief (both conditions)

"You lost your main computer. Each task folder is the surviving
project copy. Decide whether the project can be reconstructed: name
the blocking item, show the file and line that proves it, and say the
next action in your own words. After you apply the fix, decide whether
the problem is resolved or still uncertain. Think aloud at all times."

## Conditions

- Manual: task folder only. No assistant output.
- PHOENIX: task folder + printed PHOENIX first-run report; after the
  fix, printed Recovery Delta. The report may abstain — "I don't know
  yet" is a valid outcome to report, not a failure.

Order randomized per participant (coin flip); scenarios A/B assigned
so each participant sees manual once and PHOENIX once.

## Stopwatch procedure (per task T1–T6)

Start the timer the moment the fixture (or report page for the
PHOENIX condition) is placed in front of the participant. Stop when
they give their final answer for that task. Record seconds as an
integer. T2 (incorrect assumptions): count every false statement the
participant makes before their final answer, whether retracted or
not — do not correct them mid-task.

## Tasks

- T1: which item blocks reconstruction? (score 2 = correct + cited)
- T2: number of false statements before the final answer (count)
- T3: show the supporting file + line (score 2 = exact)
- T4: state the next action in own words (graded: matches fix sheet?)
- T5: after the fix, resolved or still uncertain? (score 2 = correct)
- T6: explain the result to a non-technical colleague in one minute
  (score 2 = no unexplained jargon + correct conclusion)

## Scoring rubric (0/1/2, per protocol)

2: correct + cited evidence. 1: correct, no citation. 0: wrong. T2
records a raw count instead of 0/1/2.
