# Performance forensics matrix (P01–P50)

Environment for all local numbers: Python 3.14.4, Windows AMD64, 16 CPUs,
measured 2026-11-07 with `local-tests/bench.py` unless noted.
Cross-version: suite green on local 3.14.4; CI covers 3.13 and 3.14
(the local 3.12/3.13 installs are corrupt launcher entries, unusable).
Timings are developer-tooling measurements only and must never be
presented as Uliya/NAS latency.

Verdict key: MEASURED (number below) · INSPECTED (code/design review, no
dynamic bottleneck possible at this scale) · NOT APPLICABLE (no such
subsystem locally) · BLOCKED-NAS (needs the real device).

## Filesystem and I/O

- P01 traversal cost: MEASURED — 43-file scope 13.4 ms mean (σ 0.96, n=5);
  200-filler scope 54.7 ms. ~Linear, no bottleneck.
- P02 depth/result limits: MEASURED — harness caps discovery at
  `MAX_DEPTH = 12`, reports capped entries, and degrades to PARTIAL
  (tested). NAS-side `find` limits remain the experts' own (catalog:
  `max-depth`, `limit`).
- P03 repeated discovery: MEASURED — one discovery per run; repeats across
  runs are intentional (repeatability measurement). No cache needed at 13 ms.
- P04 full-file hashing: MEASURED — sha256 is 4.0 ms of the 13.4 ms run
  (30%). Justified: hashes are integrity evidence. No change.
- P05 metadata queries: MEASURED (aggregate) — one stat pass via rglob;
  included in the 13.4 ms total. Negligible.
- P06 large files: MEASURED — `sha256_of` streams in 64 KiB chunks; a
  1.3 MB single-doc unit runs correctly in 32 ms. No bottleneck.
- P07 path normalization: MEASURED — 10k `safe_join` = 1308.5 ms
  (~0.13 ms each, `resolve()` dominates). < 1 ms per case at ≤ 5
  requirements. Documented scaling note; no action.
- P08 many irrelevant files: MEASURED — 200-filler run correct in 54.7 ms.
- P09 unicode/unusual paths: MEASURED — non-ASCII version strings covered
  in unit tests; two unicode filenames committed in `edge/` with a
  reviewed-coverage assertion. Closed.
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
- P25 version compare: MEASURED — 100k ops in 317.6 ms (~3.2 µs/op,
  includes the per-compare sha256 tail that prevents long-version
  collisions). Irrelevant at ≤ dozens of requirements per case.
- P26 duplicate structures: NOT PURSUED — evidence lists hold ≤ dozens
  of small dicts.
- P27 report generation: MEASURED (aggregate) — inside the 13.4 ms run.
- P28 temp artifacts: INSPECTED — `TemporaryDirectory` auto-cleaned;
  regenerated ZIPs are gitignored build outputs.
- P29 growth across runs: MEASURED — 5-run stdev 0.96 ms, no growth
  signal; mutant runs use fresh processes.
- P30 interruption: INSPECTED — no locks/state files; a kill leaves at
  most a half-written regenerable report.

## Concurrency and reliability

- P31/P32/P35/P37/P40: NOT APPLICABLE — single-threaded local tooling;
  NAS orchestration semantics are BLOCKED-NAS.
- P33 timeouts: NOT APPLICABLE — no operation exceeds ~55 ms locally.
- P34 retries: NOT APPLICABLE — deterministic local functions either
  return or raise; no flaky I/O retried silently.
- P36 rate/expert limits: BLOCKED-NAS — no published per-skill quota
  found in the kit; listed in the support request.
- P38 parallel-test contention: MEASURED — CI runs ubuntu+windows jobs
  in parallel, both green (run 42398606486).
- P39 repeated approvals: NOT APPLICABLE locally — one optional save
  per run by Skill design; NAS approval UX is BLOCKED-NAS.

## Developer tooling and delivery

- P41 checker time: MEASURED — 59 ms wall.
- P42 CI runtime: MEASURED — checker 10 s, ubuntu tests 12 s,
  windows tests 22–27 s (incl. runner setup), run 42400074403 (5 jobs:
  checker + 3.13/3.14 × ubuntu/windows). No redundant jobs: each cell
  covers a distinct OS/version pair.
- P43 corpus generation: ~1 s observed, not separately timed.
- P44 measurement noise: MEASURED — 7% stdev on the scale run.
- P45 report size: MEASURED — 9 files, 15769 bytes, max 4736 bytes
  (baseline-comparison.md).
- P46 packaging: MEASURED — 2.4 ms, 7372 bytes (limit is 10 MB).
- P47 markdown loading: MEASURED (aggregate) — per-doc `read_text`,
  inside run totals.
- P48 regeneration: INSPECTED — reports/wave1 regenerate on every
  runner invocation; tests read fresh outputs.
- P49 clean-checkout setup: MEASURED (proxy) — CI ubuntu job 8 s
  including checkout and Python setup.
- P50 user-request-to-report latency: BLOCKED-NAS — the harness-only
  13.4 ms is explicitly NOT user latency and must never be cited as such.

## Conclusion

No bottleneck affecting user experience was found. The dominant local
cost is path resolution (`safe_join`, ~0.13 ms/call), irrelevant below
thousands of requirements. Version comparison costs ~3.2 µs/op after
the collision-proof hash tail — also irrelevant at ≤ dozens of
requirements per case. P09 is closed; no OPEN local perf gaps remain.
