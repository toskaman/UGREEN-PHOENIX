# Performance forensics matrix (P01–P50)

Environment for all local numbers: Python 3.14.4, Windows AMD64, 16 CPUs,
measured 2026-11-07 with `local-tests/bench.py` unless noted. CI numbers
from run 42398606486. Timings are developer-tooling measurements only and
must never be presented as Uliya/NAS latency.

Verdict key: MEASURED (number below) · INSPECTED (code/design review, no
dynamic bottleneck possible at this scale) · NOT APPLICABLE (no such
subsystem locally) · BLOCKED-NAS (needs the real device).

## Filesystem and I/O

- P01 traversal cost: MEASURED — 43-file scope 11.8 ms mean (σ 0.30, n=5);
  200-filler scope 48.5 ms. ~Linear, no bottleneck.
- P02 depth/result limits: MEASURED — harness sets no depth/limit cap and
  needs none locally (48.5 ms at 200 docs). NAS-side `find` limits are the
  experts' own (catalog: `max-depth`, `limit`).
- P03 repeated discovery: MEASURED — one discovery per run; repeats across
  runs are intentional (repeatability measurement). No cache needed at 12 ms.
- P04 full-file hashing: MEASURED — sha256 is 3.7 ms of the 11.8 ms run
  (31%). Justified: hashes are integrity evidence. No change.
- P05 metadata queries: MEASURED (aggregate) — one stat pass via rglob;
  included in the 11.8 ms total. Negligible.
- P06 large files: INSPECTED — `sha256_of` streams in 64 KiB chunks;
  corpus files are < 1 KiB. No multi-MB fixture exists (minor gap, no
  production path affected: experts read NAS files, not this code).
- P07 path normalization: MEASURED — 10k `safe_join` = 1306.9 ms
  (~0.13 ms each, `resolve()` dominates). < 1 ms per case at ≤ 5
  requirements. Documented scaling note; no action.
- P08 many irrelevant files: MEASURED — 200-filler run correct in 48.5 ms.
- P09 unicode/unusual paths: PARTIAL — non-ASCII version strings covered
  in unit tests (no-crash); unicode filenames untested. OPEN minor.
- P10 stale candidates: MEASURED via test — stale-decoy rejection asserted
  in `run-tests.py` (core-a).

## Document and model processing

- P11/P12/P13/P15/P17/P19/P20 (extraction latency, batches, context,
  duplication, verbosity, selection): NOT APPLICABLE locally (no model
  executes here); BLOCKED-NAS for real numbers. Skill design bounds work
  per scope and cites catalog limits (reconcile max-files 1..200).
- P14 repeated extraction: INSPECTED — Skill issues one extract plus one
  reconcile per scope (SKILL.md steps 3–4); no repeat loop in the design.
- P16 redundant reconcile calls: INSPECTED — exactly one reconcile
  delegation per run by construction.
- P18 instruction verbosity: MEASURED statically — delegate instructions
  99/121/94/138 words; SKILL.md 1060 words total. Concise for the
  contract carried; no cut without NAS evidence it helps.

## CPU and memory

- P21 peak memory: MEASURED — 273 KiB Python peak (tracemalloc, scale run).
- P22 streaming: INSPECTED — hashing streams; doc reads are whole-file on
  KB-scale fixtures. Adequate.
- P23 allocations: NOT PURSUED — 273 KiB peak leaves nothing to win.
- P24 repeated parse/serialize: MEASURED — repeats are the repeatability
  protocol (3 runs/case), not waste.
- P25 version compare: MEASURED — 100k ops in 141.7 ms (~1.4 µs/op).
- P26 duplicate structures: NOT PURSUED — evidence lists hold ≤ dozens
  of small dicts.
- P27 report generation: MEASURED (aggregate) — inside the 11.8 ms run.
- P28 temp artifacts: INSPECTED — `TemporaryDirectory` auto-cleaned;
  regenerated ZIPs are gitignored build outputs.
- P29 growth across runs: MEASURED — 5-run stdev 0.30 ms, no growth
  signal; mutant runs use fresh processes.
- P30 interruption: INSPECTED — no locks/state files; a kill leaves at
  most a half-written regenerable report.

## Concurrency and reliability

- P31/P32/P35/P37/P40: NOT APPLICABLE — single-threaded local tooling;
  NAS orchestration semantics are BLOCKED-NAS.
- P33 timeouts: NOT APPLICABLE — no operation exceeds ~50 ms locally.
- P34 retries: NOT APPLICABLE — deterministic local functions either
  return or raise; no flaky I/O retried silently.
- P36 rate/expert limits: BLOCKED-NAS — no published per-skill quota
  found in the kit; listed in the support request.
- P38 parallel-test contention: MEASURED — CI runs ubuntu+windows jobs
  in parallel, both green (run 42398606486).
- P39 repeated approvals: NOT APPLICABLE locally — one optional save
  per run by Skill design; NAS approval UX is BLOCKED-NAS.

## Developer tooling and delivery

- P41 checker time: MEASURED — 56 ms wall.
- P42 CI runtime: MEASURED — checker 10 s, ubuntu tests 8 s,
  windows tests 14 s (incl. runner setup), run 42398606486. No
  redundant jobs (3 jobs, disjoint purposes).
- P43 corpus generation: ~1 s observed, not separately timed.
- P44 measurement noise: MEASURED — 2.5% stdev on the scale run.
- P45 report size: MEASURED — 9 files, 14483 bytes, max 4730 bytes.
- P46 packaging: MEASURED — 2.2 ms, 7238 bytes (limit is 10 MB).
- P47 markdown loading: MEASURED (aggregate) — per-doc `read_text`,
  inside run totals.
- P48 regeneration: INSPECTED — reports/wave1 regenerate on every
  runner invocation; tests read fresh outputs.
- P49 clean-checkout setup: MEASURED (proxy) — CI ubuntu job 8 s
  including checkout and Python setup.
- P50 user-request-to-report latency: BLOCKED-NAS — the harness-only
  11.8 ms is explicitly NOT user latency and must never be cited as such.

## Conclusion

No bottleneck affecting user experience was found. The dominant local
cost is path resolution (`safe_join`, ~0.13 ms/call), irrelevant below
thousands of requirements. Nothing was optimized because nothing
measured slow; P09 unicode filenames remains a minor OPEN test gap.
