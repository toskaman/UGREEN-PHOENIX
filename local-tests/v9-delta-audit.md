# v9 delta audit (Phase Alpha) — ranked critical-first

Workflow audit of v8 (`8b32ab0`), 7/7 scopes complete + critic +
synthesis. Static enumeration only (READ-ONLY workflow); every count
below was re-verified live by `local-tests/check_consistency.py`
(suites re-run, baseline regenerated, docs matched).

Exit condition: no unresolved critical contradiction in the native
Skill, proposal, package, or public claims — MET (D1–D7 + X1–X10
fixed and verified; D8–D30 pass with no fix).

## Critical

### D1 — devpost-kit stale counts (FIXED)
- Source: `local-tests/devpost-kit.md:32-33`
- Repro: read lines 32-33 vs `README.md:120-123` + `mutate.py` (17 mutants)
- Expected: 91/91 checks, 17/17 kills (also required by devpost-kit `:4-6`
  exact-match claim)
- Actual: stated 86/86, 16/16
- Fix: updated to 91/91, 17/17, then 92/92 (Beta planner check)
- Regression: `check_consistency.py` asserts devpost-kit numbers live
- Evidence: checker output `consistency OK`

### D2 — local builder kit unpinned (FIXED)
- Source: `A SOUMETTRE/build_zip.py:19`
- Repro: builder ran hardcoded local checker with no version/hash assert;
  `SHA256SUMS.txt` hashes deliverables only; `audit-matrix.md:445`
  overclaimed "pinned" citing CI only
- Expected: local path pinned exactly like CI
- Actual: a swapped local kit ran unchecked
- Fix: builder asserts kit zip sha256
  `cf557e5a…e1b3` + `catalogVersion == 2.0.0`; audit-matrix Q085
  corrected to cite both pins
- Regression: builder fails loudly on kit swap (assert before zip)
- Evidence: `kit pinned: uliya-skill-kit-0.7.3-en.zip … catalog=2.0.0`

## High

### D3 — builder measured compressed bytes vs kit uncompressed rule (FIXED)
- Source: `A SOUMETTRE/build_zip.py:38` vs kit `check-lib.mjs:15,179,213,235`
- Repro: builder asserted zip `< 10_000_000`; kit sums uncompressed
  `metadata.size ≤ 10485760` — stricter number, different quantity
- Expected: assert the kit's quantity
- Actual: only the embedded checker run closed the gap
- Fix: builder pre-asserts uncompressed total `≤ 10485760`
- Regression: same builder gate; checker re-verifies
- Evidence: `uncompressed total bytes: …` builder line

### D4 — builder glob dropped nested references (FIXED)
- Source: `A SOUMETTRE/build_zip.py:27` vs kit `walkReferences` (`:246-287`)
- Repro: top-level `glob("*.md")` while kit permits nested subdirs
- Expected: package everything the kit allows
- Actual: nested `.md` silently dropped
- Fix: recursive `rglob("*.md")`
- Regression: exact-namelist assert still guards contents
- Evidence: builder run green, checker `static-pass`

## Medium

### D5 — no per-file size assert (FIXED)
- Source: `A SOUMETTRE/build_zip.py` (missing) vs kit `:14,214-222`
- Fix: assert each input `≤ 1048576` before zipping. Indirect checker
  coverage retained as second layer.

### D6 — no file-count assert (FIXED)
- Source: `A SOUMETTRE/build_zip.py` (missing) vs kit `:16,227-234`
- Fix: assert `len(files) ≤ 100` before zipping. Checker re-verifies.

### D7 — 92/92 needs symlink privileges (FIXED, documented)
- Source: `local-tests/run-tests.py:676-682` + `README.md:120`
- Repro: `overflow-b` check runs only `if linked:`; otherwise suite
  prints 91 ALL GREEN (92 with the Beta planner check)
- Fix: README footnotes 92/92 as symlink-capable-only (91 otherwise)
- Evidence: README note; checker runs live on this host (91)

## Low — verified pass, no fix (D8–D30)

D8 README counts match static enumeration (92/92, 147/147, 39/39,
31/31, 35/35, 20/20, 17/17). D9 run-tests 85 check lines with `:447`
×8 = 92 (84 lines = 91 at audit time, +1 Beta planner check). D10 aggregate 7+23+3+4+4+2+15+4+80+5 = 147. D11 proofgraph
now 3+4+6+1+5+12+2+2+2+2 (v9) = 39. D12 harness 8+6+7+2+8 = 31.
D13 budget 11 scenarios = 35. D14 contract 20 `check(` calls = 20 (19 + Zeta checklist pin).
D15 `MUTANTS` 17 entries. D16 baseline 6×8 grid matches README,
build_pdf, devpost-kit. D17 `RUNS=3` matches report. D18 6 METHODS
match report. D19 headers verbatim. D20 labels.json 8 cases (5
blocker / 2 abstain). D21 corpus REQUIRES total 22. D22 summary cells
recomputed from per-case verdicts. D23 baselines.py matches report
preamble. D24 build_pdf claims verified (50 held-out = 44+6, locked
10/10, 12-case transfer). D25 evidence-index sizes/CI match
PROVENANCE + disk. D26 build_pdf asserts (≤500 words, <1MB, ≤2
pages) verified. D27 kit limits 1048576/10485760/100 enumerated.
D28 CI kit URL+sha pinned, catalog 2.0.0 enforced, recorded
`static-pass`. D29 assistant-vs-phoenix has zero numeric baseline
claims (vacuous match). D30 local-simulation-only labels correct;
ms/case formula correct, values timing-dependent.

## Extended — native contract + renderer (X1–X10, all FIXED)

### X1 — Passport placement vs "exactly 8 sections"
- Source: `SKILL.md:46,51` + `references/report-contract.md:49-60`
- Actual: "close with a Passport" + "exactly these sections" + "8
  sections above" left placement ambiguous
- Fix: SKILL states Passport appendix AFTER the 8 sections, §9
  reserved for Delta; contract carries a Placement paragraph
- Evidence: 20/20 contract suite green (19 + Zeta checklist pin)

### X2 — protocol item 9 vs exactly-8
- Source: `references/decision-protocol.md:20-30` item 9
- Fix: items 9/10 reworded as rules for §7 / §9, not sections

### X3 — step-4 RESULT → documentary-state mapping missing
- Source: `SKILL.md:43` vs `decision-protocol.md:5-10`
- Actual: PRESENT/ABSENT/UNRESOLVED had no explicit mapping to
  FOUND/NOT FOUND IN SCOPE/UNKNOWN
- Fix: translation block in SKILL step-5 + protocol
  `## Verification-result translation`

### X4 — REQ constraint suffix vs "mirror exactly"
- Source: `local-tests/proofgraph.py:35-38,46` vs
  `references/report-contract.md:15`
- Fix: contract documents `[REQ: subject OP version]` as the
  version-constrained form

### X5 — FACT missing from node-constant tuple
- Source: `local-tests/proofgraph.py:27` vs `:55`
- Fix: `FACT` added to the tuple

### X6 — FILE-vs-FACT rule diverged from harness
- Source: `local-tests/proofgraph.py:52` vs `harness.py:371-372`
- Actual: dotted+version-constrained capability rendered `[FILE:]`
- Fix: op-aware rule (`"." + op set → FACT`); residual: harness also
  excludes provision-names, unknowable to the renderer — documented,
  no corpus case hits it
- Regression: new `test_proofgraph.py` FACT check (39/39)

### X7 — delta passport merged §§5-6
- Source: `local-tests/proofgraph.py:142` vs contract `:56-58`
- Fix: renderer emits separate §5 (delta graph) + §6 (transition
  history); A/B/C renders rebuilt (split-only diffs)
- Regression: new `test_proofgraph.py` §§5-6 check (39/39)

### X8 — delta-state vocabulary 4 vs 9
- Source: `references/report-contract.md:41-44` vs `harness.py:502-522`
- Fix: contract enumerates the exhaustive 9-state vocabulary with
  definitions; protocol item 10 points at it

### X9 — runbook corpora vs validation-plan families
- Source: `local-tests/finalist-runbook.md:34-43` vs
  `references/validation-plan.md`
- Fix: runbook carries an explicit corpus→family mapping table note

### X10 — §7 wording drift
- Source: `local-tests/closure-demo.md:100` ("§7 recommendations")
- Fix: "§7 Next steps" to match `harness.py:613`

## Carried caveats (not contradictions)

- Runtime suite outputs in the workflow were statically enumerated;
  `check_consistency.py` now re-runs them live (92/92 observed).
- Mean ms/case values are timing-dependent (formula verified).
- `CLEAR` shorthand in closure-demo vs full verdict strings: harmless
  shorthand, both sides verified present.
- Devpost rules pages returned HTTP 403 to direct fetch (as in prior
  cycles); rules verified against the pinned local kit + prior mirrors.
