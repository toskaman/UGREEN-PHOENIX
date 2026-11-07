# PHOENIX local tests (simulation only)

This folder validates the PHOENIX **workflow logic** on a synthetic local
corpus. It is NOT a NAS runtime test and proves nothing about Uliya experts,
NAS permissions, or model quality on a real device.

## Layout

- `corpus/core-a/` — synthetic project whose deployment guide requires an
  absent `config/prod-config.yaml` (expects `NOT FOUND IN SCOPE`).
- `corpus/core-b/` — synthetic project whose `runtime.yaml` declares
  `runtime 2.4.1` against a required `runtime >= 3.0` (expects `CONFLICTING`).
- `corpus/edge/` — access-denied file, truncated document, an embedded
  instruction that must be ignored, and unicode filenames (expects
  `INSUFFICIENT EVIDENCE`).
- `corpus/core-a/old-backup/` — stale decoy copy: same basename, wrong
  location (must stay `NOT FOUND IN SCOPE`).
- `corpus/core-c/` — healthy project, every requirement satisfied (expects
  `NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES`).
- `corpus/core-d/` — mixed evidence: one `FOUND`, one `NOT FOUND IN SCOPE`,
  one `CONFLICTING`.
- `corpus/edge-2/` — two guides disagree on the required runtime version.
- `corpus/edge-3/` — denied file referenced by `REQUIRES`, plus traversal
  and absolute subjects that must be rejected without resolving.
- `corpus/scale/` — 40 filler docs plus 5 requirements (coverage + timing).
- `harness.py` — simulates discover → extract → verify → report and emits a
  PHOENIX-style evidence report with verdict, completion state
  (`COMPLETED`/`PARTIAL`), plain-language verdict line, depth cap, OS-error
  mapping, secret redaction, prioritized recommendations, and Recovery
  Closure rechecks (prior report in, §9 Recovery Delta out).
- `run-tests.py` — runs the harness on all corpora and asserts the exact
  labels required by `references/validation-plan.md`, plus helper units,
  a SKILL/report vocabulary guard, and the 8-section report contract.
- `baselines.py` + `run-baseline.py` — a cited retrieval-plus-analysis
  method that abstains on unfounded versions, naive filename search, and
  generic QA, plus two PHOENIX ablations (no reconciliation, no
  verification), scored on predeclared `labels.json` ground truth with
  extended precision/recall metrics.
- `prompts.json` + `rehearse-wave1.py` — validated wave-1 prompt pack and
  session-artifact generator (prompt pack, predicted reports, run log,
  scoring sheet, upload ZIP).
- `wave1/` — generated wave-1 artifacts (regenerate with `rehearse-wave1.py`).
- `finalist-runbook.md` — hour-by-hour 24-hour NAS session plan.
- `demo-script.md` — timed 3-minute demo narration and recording checklist.
- `wave1-support-request.md` — send-ready support message with the 11 questions.
- `wave1-session-checklist.md` — one-page session tick list.
- `open-questions-for-ugreen.md` — platform questions for the support team.
- `reports/` — generated reports (regenerate with `run-tests.py` and
  `run-baseline.py`).
- `mutate.py` — mutation testing: 14 mutants (harness single-point, a
  double mutant, a baselines mutant), all must be killed by the suite
  (measured kill rate, also runs in CI).
- `bench.py` + `perf-matrix.md` — local performance measurements and the
  P01–P50 matrix (measured vs. not-applicable vs. blocked-on-NAS).
- `evidence-check-result.json` — real output of the official static checker
  (`static-pass`, 0 errors, 0 warnings).
- `audit-matrix.md` — 100-question forensic audit (40 PASS / 46 PARTIAL /
  2 FAIL / 12 UNKNOWN) with evidence pointers.
- `jury-report.md` — independent adversarial panel scores with agreements,
  splits, TOPFIX disposition, and post-Cycle-3 reassessment.
- `commercial-thesis.md` — research-backed business thesis + P2 log.
- `evidence-index.md` — content hashes and artifact provenance.
- `audit-delta.md` — OMEGA delta audit (D001–D050: prize fit, Devpost
  surface, supply chain, hidden debt, failure shape).
- `jury-questions.md` — 50 hardest jury questions with evidence-backed
  answers (Devpost FAQ source).
- `devpost-kit.md` — paste-ready Devpost drafts (human-gated upload).
- `make-scale-corpus.py` — deterministic scale-corpus generator.
- `closure-demo.md` — flagship "The Recovery That Looked Complete" walkthrough
  (scenarios A/B/C with reproduce recipes).

## Run

```sh
python run-tests.py       # 71 acceptance checks (must be ALL GREEN)
python run-baseline.py    # baseline comparison → reports/baseline-comparison.md
python rehearse-wave1.py  # validate prompts, regenerate wave1/ artifacts
```

## Honesty rules

- Local green tests never become NAS claims. The main README reports them
  only as "local workflow-logic simulation".
- No corpus file is read outside its case scope; denied files are never
  opened (verified by a no-leak assertion).
- Embedded instructions in corpus documents are untrusted text and are never
  executed (verified by assertions on the report content).
