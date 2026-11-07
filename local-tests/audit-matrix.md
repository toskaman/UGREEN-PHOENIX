# 100-question forensic audit matrix

Tree: `c44c4dd` (Cycle 4) unless noted. Verdict key: PASS
(proven by cited evidence), PARTIAL (proven in one layer, open in
another), FAIL (does not hold), UNKNOWN (no evidence either way),
NOT APPLICABLE. Local simulation never counts as NAS evidence.

## A. Hackathon compliance and technical feasibility

### Q001 — Skill follows Uliya standard — PASS
- Finding: static checker `static-pass`, 0 errors/warnings on exact bytes.
- Evidence: `local-tests/evidence-check-result.json` (protocol sha `e4cf314c…` matches tree).
- Risk: low. Status: VERIFIED. Test: checker re-run after every Skill edit + CI job.

### Q002 — Name, frontmatter, layout valid — PASS
- Finding: `name: phoenix-recovery-intelligence` matches directory; checker enforces.
- Evidence: `SKILL.md:1-4`, CI packaging assert (`.github/workflows/ci.yml:50-61`).
- Risk: low. Status: VERIFIED.

### Q003 — Referenced CLI actions exist in catalog — PASS
- Finding: all 9 actions (`find/ls/stat/sha256sum`, `qa/extract/reconcile`,
  `collect-evidence/save-text`) verified in catalog 2.0.0; NAS-fit judge re-verified with line numbers.
- Evidence: `dev-kit/extracted/uliya-skill-kit/data/capability-catalog.json` (gitignored kit).
- Risk: low. Status: VERIFIED.

### Q004 — Delegations target correct experts — PASS
- Finding: 4 delegations → `file-agent` (2×), `document-agent`, `knowledge-agent`.
- Evidence: `SKILL.md:30-37`. Risk: low. Status: VERIFIED (static).

### Q005 — Input params grounded — PARTIAL
- Finding: scope/scenario/goal come from the user (`SKILL.md:14-16`); vague
  params ("bounded selection") rely on expert judgment, unexecuted.
- Evidence: `SKILL.md:29-37`. Risk: medium — expert may under-select.
- Improvement: runbook W1 probes selection breadth. Status: OPEN, BLOCKED-NAS.

### Q006 — No implied unsupported capabilities — PASS
- Finding: explicit disclaimers; no snapshot/backup/OS-restore/monitor implied.
- Evidence: `SKILL.md:10`, `README.md:135-136`, `references/disclosures.md:10`.
- Risk: low. Status: VERIFIED.

### Q007 — Package files and references compliant — PASS
- Finding: SKILL.md + 3 directly linked references/*.md; checker validates links.
- Evidence: checker `files[]` (4 entries), CI zip-contents assert.
- Risk: low. Status: VERIFIED.

### Q008 — Completion/failure/approval states — PARTIAL
- Finding: all states handled in prose (`SKILL.md:42-48`); save/approval and
  real failure paths unexecuted.
- Evidence: `SKILL.md:42-48`; local completion model (`harness.py` COMPLETED/PARTIAL + 2 checks).
- Risk: medium. Status: OPEN, BLOCKED-NAS for platform half.

### Q009 — Disclosures accurate — PASS
- Finding: AI assistance (ChatGPT, Muse Code), kit 0.7.3, no bundled code disclosed.
- Evidence: `references/disclosures.md`, `README.md:146-153`.
- Risk: low. Status: VERIFIED.

### Q010 — Package matches tested commit — PASS
- Finding: release rebuilt from the final tree with per-file verification and
  SHA-256 manifest outside the ZIP.
- Evidence: `A SOUMETTRE/SHA256SUMS.txt` (gitignored) + final report hashes.
- Risk: low. Status: VERIFIED at release time.

## B. Architecture and orchestration

### Q011 — Parent is pure orchestration — PASS
- Finding: parent holds no business logic; all execution delegated.
- Evidence: `SKILL.md:25,29-37`. Risk: low. Status: VERIFIED (static).

### Q012 — Clean expert separation — PASS
- Finding: filesystem=discovery/verify, document=extract/reconcile, knowledge=report.
- Evidence: `SKILL.md:30-37`. Risk: low. Status: VERIFIED (static).

### Q013 — Explicit completion gates — PASS
- Finding: "Only after discovery is `completed`" gates steps 3–5.
- Evidence: `SKILL.md:32,36`. Risk: low. Status: VERIFIED (static).

### Q014 — No consumption of unverified upstream results — PARTIAL
- Finding: prose forbids inventing paths/substitution; no programmatic gate
  (platform-owned execution).
- Evidence: `SKILL.md:32-33,42`. Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q015 — Delegated instructions self-contained and scoped — PASS
- Finding: each instruction repeats scope + read-only + no-broadening.
- Evidence: `SKILL.md:31,33,35,37`. Risk: low. Status: VERIFIED (static).

### Q016 — Decision protocol precise enough — PARTIAL
- Finding: 5 labels + ordering + output contract are precise; cross-run
  consistency unmeasured without a model.
- Evidence: `references/decision-protocol.md`; local 8/8 stable ×3 runs.
- Risk: medium. Status: OPEN, BLOCKED-NAS for model variance.

### Q017 — Safe recovery from partial failure — PARTIAL
- Finding: `failed` rule preserves partial evidence and stops dependents;
  real partial-failure behavior unobserved.
- Evidence: `SKILL.md:43`. Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q018 — Explicit stable data contracts — PASS
- Finding: one-line formats (`PATH, BYTES, SHA256`; `SUBJECT, CONSTRAINT,
  SOURCE-PATH, LOCATION`; `SUBJECT, RESULT, PATH-OR-SCOPE, DETAIL`).
- Evidence: `SKILL.md:31,33,35`. Risk: low. Status: VERIFIED (static).

### Q019 — Not unnecessarily complex — PASS
- Finding: 4 delegations, linear pipeline, no branching framework.
- Evidence: `SKILL.md:29-37`. Risk: low. Status: VERIFIED (static review).

### Q020 — Could it be simpler — PARTIAL
- Finding: verify step could merge into discovery, but ablation shows it
  catches stale-decoy false clears (`phoenix_no_verify` 6/8 + 1 false clear).
- Evidence: `local-tests/reports/baseline-comparison.md:19,30`.
- Risk: low. Status: VERIFIED — simplification rejected with evidence.

## C. Functional correctness (local logic proven; model behavior UNKNOWN)

### Q021 — Identify genuinely missing dependency — PARTIAL
- Finding: local PASS (core-a `NOT FOUND IN SCOPE`, no global claim).
- Evidence: `run-tests.py` core-a block; NAS half UNKNOWN.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q022 — Missing vs out-of-scope — PARTIAL
- Finding: label semantics enforce the distinction locally; expert scope
  discipline UNKNOWN.
- Evidence: `references/decision-protocol.md:7`, stale-decoy check.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q023 — Detect incompatible versions — PARTIAL
- Finding: local PASS (core-b, edge-2 CONFLICTING with both sources cited).
- Evidence: `run-tests.py` core-b/edge-2 blocks; reconcile quality UNKNOWN.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q024 — Same-name files across locations — PARTIAL
- Finding: local PASS (stale decoy rejected by exact path).
- Evidence: core-a decoy check. NAS same-name behavior UNKNOWN.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q025 — Conflicting requirements from two documents — PARTIAL
- Finding: local PASS (edge-2 guides disagree → CONFLICTING).
- Evidence: `run-tests.py` edge-2 block. Multi-doc reconcile UNKNOWN.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q026 — Multiple valid alternative dependencies — PARTIAL
- Finding: any-satisfying-provision resolves FOUND (temp-dir unit); the
  non-satisfying alternative is not surfaced as such in the report.
- Evidence: `run-tests.py` alternatives unit. Model behavior UNKNOWN.
- Risk: low. Improvement: list unused alternatives in §6. Status: OPEN (minor).

### Q027 — Required vs optional asset — FAIL
- Finding: marker spec and protocol have no optional-dependency syntax;
  everything extracted is treated as required.
- Evidence: absence in `harness.py:8-12`, `references/decision-protocol.md`.
- Risk: medium — optional items can false-blocker. Improvement: `REQUIRES-OPTIONAL`
  + `edge-4` corpus. Status: OPEN (future work).

### Q028 — Existence vs readability vs compatibility vs recoverability — PARTIAL
- Finding: distinguished locally (FOUND / INACCESSIBLE / CONFLICTING /
  never-claimed-restore); NAS behavior UNKNOWN.
- Evidence: `run-tests.py` edge-3/core-b/assertion blocks.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q029 — Honest insufficient-evidence verdict — PARTIAL
- Finding: local PASS (edge, edge-3 → INSUFFICIENT, never forced).
- Evidence: `run-tests.py` edge/edge-3 blocks. Model abstention UNKNOWN.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q030 — Verdicts traceable to evidence — PARTIAL
- Finding: 22/22 rows cited with source:line locally; NAS citation
  fidelity UNKNOWN.
- Evidence: `local-tests/reports/baseline-comparison.md:17`.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

## D. Security, privacy and adversarial robustness

### Q031 — Read outside authorized scope — PARTIAL
- Finding: local containment tested (`safe_join`, manifest normalization,
  traversal rejection); expert containment is prose-only, unexecuted.
- Evidence: `run-tests.py` safe_join/traversal checks; `SKILL.md:29,31`.
- Risk: high if violated. Status: OPEN, BLOCKED-NAS for expert half.

### Q032 — Symlinks, traversal, resolved paths — PASS
- Finding: symlinks never followed (live conditional test incl.
  no_verify-leak assertion), traversal/absolute rejected, resolve-checked.
- Evidence: `harness.py:61-71,109-123`, `run-tests.py` edge-3 + symlink block.
- Risk: low. Status: VERIFIED (59/59 green incl. live symlink run).

### Q033 — Hostile content changing instructions — PARTIAL
- Finding: local parser only reads markers (injection corpus ignored);
  MODEL prompt-injection resistance untested — the real risk.
- Evidence: `run-tests.py` injection check; runbook W1-G injection scenario planned.
- Risk: high. Status: OPEN, BLOCKED-NAS.

### Q034 — Document-requested writes/deletion/expansion — PARTIAL
- Finding: read-only delegations + no-broadening prose; enforcement UNKNOWN.
- Evidence: `SKILL.md:31,33,35`. Risk: high. Status: OPEN, BLOCKED-NAS.

### Q035 — Approval requirements preserved — PARTIAL
- Finding: prose gate (`waiting_approval`, no write until confirmed);
  save path never executed.
- Evidence: `SKILL.md:37,46`. Risk: high. Status: OPEN, BLOCKED-NAS.

### Q036 — Secret exposure via reports/errors — PARTIAL
- Finding: 6 keyword classes + 3 token prefixes redacted and tested;
  novel secret shapes (custom tokens, keys in prose) uncovered.
- Evidence: `harness.py:40-49`, redact unit, no-leak checks (98452, 77341).
- Risk: medium (residual). Improvement: entropy-based fallback. Status: OPEN (minor).

### Q037 — Fabricated paths/citations — PARTIAL
- Finding: impossible in the harness (citations constructed from observed
  paths); MODEL fabrication is the untested risk.
- Evidence: `harness.py:243-265` construction; no model runs.
- Risk: high. Status: OPEN, BLOCKED-NAS.

### Q038 — Denied vs timeout outcomes differ — PARTIAL
- Finding: denied → INACCESSIBLE locally; harness has no timeout concept;
  NAS denied/timeout signaling UNKNOWN (support question Q4).
- Evidence: `run-tests.py` edge-3; `wave1-support-request.md`.
- Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q039 — Malicious content treated as untrusted — PARTIAL
- Finding: local markers-only parsing ignores prose; model discipline UNKNOWN.
- Evidence: injection corpus; `SKILL.md:49`, `decision-protocol.md:27`.
- Risk: high. Status: OPEN, BLOCKED-NAS.

### Q040 — Privacy/local-model claims evidenced — PARTIAL
- Finding: no on-device claim is made (honest UNKNOWN stated); third-party
  reviews report on-device Uliya but possible cloud egress — unresolved.
- Evidence: `README.md:141-144`; commercial thesis §8 with sources.
- Risk: medium. Status: OPEN, BLOCKED-NAS + vendor confirmation.

## E. AI quality and evidence reliability (no model runs: mostly UNKNOWN)

### Q041 — Understands natural documentation — UNKNOWN
- Finding: no model execution exists; harness parses markers only.
- Evidence: absence (honest). Risk: high. Status: BLOCKED-NAS (runbook W1-A..H).

### Q042 — Indirect multi-paragraph requirements — UNKNOWN
- Same basis as Q041. Status: BLOCKED-NAS.

### Q043 — Extracts without inventing — UNKNOWN
- Same basis; anti-invention rules exist (`SKILL.md:32-33`) but are untested.
- Status: BLOCKED-NAS.

### Q044 — Preserves source locations across delegation — UNKNOWN
- Same basis; LOCATION contract specified (`SKILL.md:33`) but untested.
- Status: BLOCKED-NAS.

### Q045 — Handles contradictory evidence — UNKNOWN (model)
- Local reconcile logic PASS (CONFLICTING ×3 cases); `ug-document
  reconcile` behavior UNKNOWN. Status: BLOCKED-NAS.

### Q046 — Recognizes retrieval uncertainty — UNKNOWN
- Abstention rules specified; model compliance untested. Status: BLOCKED-NAS.

### Q047 — Stable across repeated runs — UNKNOWN
- Deterministic layers stable (8/8 ×3 runs); model variance unmeasured.
- Status: BLOCKED-NAS.

### Q048 — Multiple languages — UNKNOWN
- Platform reportedly supports EN/DE/ZH/JA (third-party review, unverified);
  PHOENIX adds nothing language-specific; no multilingual test.
- Status: BLOCKED-NAS + vendor confirmation.

### Q049 — Avoids overconfident recovery claims — PARTIAL
- Finding: anti-overconfidence rules + local no-restored assertions PASS;
  model compliance UNKNOWN.
- Evidence: `decision-protocol.md:25-26`, `run-tests.py` no-restored checks.
- Risk: high. Status: OPEN, BLOCKED-NAS.

### Q050 — AI outperforms credible baseline held-out — UNKNOWN
- Finding: deterministic logic beats baselines 8/8 vs 6/8 vs 3/8 vs 1/8,
  but that is not an AI measurement; no held-out model runs.
- Evidence: `local-tests/reports/baseline-comparison.md` (labeled simulation).
- Risk: high. Status: BLOCKED-NAS.

## F. Testing, validation and quality assurance

### Q051 — Checks independent enough to detect real defects — PARTIAL
- Finding: 59 checks + 14/14 mutation kills prove detection for covered
  points; property/fuzz/metamorphic layers absent.
- Evidence: `mutate.py` kill log; `run-tests.py`.
- Risk: medium. Status: OPEN (minor — diminishing returns).

### Q052 — Corpora cover realistic structures — PARTIAL
- Finding: 8 corpora cover healthy/mixed/conflicting/denied/truncated/
  hostile/scale shapes but are tiny, synthetic, marker-based.
- Evidence: `local-tests/corpus/` (8 dirs). Risk: medium.
- Improvement: natural-prose corpora need a model to grade. Status: OPEN, BLOCKED-NAS.

### Q053 — Ground truth independent of implementation — PASS
- Finding: `labels.json` predeclared per case (verdict, blocker, abstain, key labels).
- Evidence: `local-tests/labels.json`. Risk: low. Status: VERIFIED.

### Q054 — Baselines fair and relevant — PARTIAL
- Finding: 6 methods incl. strong cited retrieval_plus + 2 ablations;
  still deterministic, not LLM-vs-LLM.
- Evidence: `baselines.py`, `run-baseline.py`, comparison report.
- Risk: medium. Status: OPEN (LLM baselines need NAS).

### Q055 — False-positive/negative discovery scenarios — PASS
- Finding: false clears + false blockers measured per method (phoenix 0/0;
  no_verify 1/1; filename 3/1; generic_qa 5/0).
- Evidence: `local-tests/reports/baseline-comparison.md:26-33`.
- Risk: low. Status: VERIFIED.

### Q056 — Property/fuzz/adversarial/metamorphic tests — PARTIAL
- Finding: adversarial YES (injection corpus, traversal, unsafe versions,
  jury red-team); property/fuzz/metamorphic NO.
- Evidence: `run-tests.py` nasty-version list, edge/edge-3 blocks.
- Risk: low-medium. Status: OPEN (minor).

### Q057 — Mutation kills tests — PASS
- Finding: 14/14 killed, each by its intended check, incl. double mutant
  and a baselines mutant; runs in CI.
- Evidence: `mutate.py`, CI log run 42400074403. Risk: low. Status: VERIFIED.

### Q058 — Repeatable on clean machine — PASS
- Finding: CI rebuilds ubuntu+windows × 3.13/3.14 from checkout, all green;
  stdlib-only (no pip deps).
- Evidence: `.github/workflows/ci.yml`, run 42400074403.
- Risk: low. Status: VERIFIED.

### Q059 — CI detects broken refs/packaging/regressions — PASS
- Finding: checker job + zip-contents assert + suite + baseline +
  rehearsal + mutation on every push.
- Evidence: `.github/workflows/ci.yml`. Risk: low. Status: VERIFIED.

### Q060 — NAS vs simulation distinguished — PASS
- Finding: separated in README, harness docstring, every report header,
  baseline footer, PDF, disclosures.
- Evidence: `README.md:115-124`, `harness.py:1-6`.
- Risk: low. Status: VERIFIED.

## G. Performance and resource efficiency

### Q061 — Discovery cost vs corpus size — PASS
- Finding: 13.4 ms at 43 files, 54.7 ms at 200 files — ~linear, no bottleneck.
- Evidence: `perf-matrix.md` P01, `bench.py`. Risk: low. Status: VERIFIED.

### Q062 — Large files needlessly read/hashed — PASS
- Finding: streaming 64 KiB hash; 1.3 MB doc runs in 32 ms; no full-read waste.
- Evidence: P06, `harness.py:74-79`. Risk: low. Status: VERIFIED.

### Q063 — Redundant expert calls — PASS
- Finding: one extract + one reconcile per scope by construction; no loops.
- Evidence: P14/P16, `SKILL.md:32-35`. Risk: low. Status: VERIFIED (design).

### Q064 — Unnecessary evidence into model context — UNKNOWN
- Finding: no model runs; batching bounds specified but unmeasured.
- Evidence: `SKILL.md:33` bounds. Risk: medium. Status: BLOCKED-NAS.

### Q065 — Search/processing limits explicit — PARTIAL
- Finding: local `MAX_DEPTH=12` + catalog limits cited; NAS enforcement UNKNOWN.
- Evidence: `harness.py` MAX_DEPTH, P02. Risk: low. Status: OPEN, BLOCKED-NAS.

### Q066 — Latency vs doc/dependency count — PASS (local)
- Finding: measured scaling numbers (P01/P08); model latency UNKNOWN.
- Evidence: `perf-matrix.md`. Risk: low locally. Status: VERIFIED (local).

### Q067 — Memory bounded — PASS
- Finding: 273 KiB Python peak (tracemalloc, scale run).
- Evidence: P21. Risk: low. Status: VERIFIED.

### Q068 — Measurements repeatable and qualified — PASS
- Finding: env-qualified, means + stdev over repeats, `bench.py` committed.
- Evidence: `perf-matrix.md:3-6`, P44. Risk: low. Status: VERIFIED.

### Q069 — Optimizations sacrificing completeness/security — PASS
- Finding: nothing optimized away; the hash tail ADDS cost for correctness.
- Evidence: P25 note, Q020. Risk: low. Status: VERIFIED.

### Q070 — Graceful degradation on exhaustion — UNKNOWN (model)
- Finding: local PARTIAL degradation tested (depth/errors → PARTIAL);
  model-context exhaustion UNKNOWN.
- Evidence: depth-cap unit. Risk: medium. Status: OPEN, BLOCKED-NAS.

## H. User experience and accessibility

### Q071 — Beginner understands what PHOENIX does — PARTIAL
- Finding: README + Goal + plain-language verdicts; jury: labels still jargony.
- Evidence: `README.md:6-9`, `SKILL.md:6-10`, jury-report UV.
- Risk: medium. Status: OPEN (minor).

### Q072 — Scope selection understandable — PARTIAL
- Finding: documented with example invocation; picker still manual paste-a-path.
- Evidence: `README.md:91-102`. Risk: medium. Status: OPEN (platform UX).

### Q073 — Findings translated to next actions — PARTIAL
- Finding: per-label next steps + plain sentences; jury: still generic-ish,
  no remediation actions (out of scope by design).
- Evidence: `harness.py` next_steps, protocol §7. Risk: medium. Status: OPEN.

### Q074 — Errors/denials/incomplete clearly explained — PASS
- Finding: INACCESSIBLE vs UNKNOWN vs errors distinct, each with plain sentence.
- Evidence: sample reports §2/§8. Risk: low. Status: VERIFIED (local).

### Q075 — Prioritized by consequence — PARTIAL
- Finding: fail-closed ordering (blocker > abstain > clear) + §5 blockers
  first; consequence ranking is rule-based, not user-tuned.
- Evidence: `harness.py` verdict ordering. Risk: low. Status: VERIFIED (local).

### Q076 — Expert can locate exact evidence — PASS
- Finding: every row carries source:line; both conflicting sources cited.
- Evidence: sample reports §4, 22/22 cited. Risk: low. Status: VERIFIED (local).

### Q077 — Confirmed blockers vs plausible concerns — PASS
- Finding: DOCUMENTARY BLOCKER vs suspected/incomplete (UNKNOWN) distinct
  by label + verdict ordering.
- Evidence: `decision-protocol.md:5-9`. Risk: low. Status: VERIFIED (local).

### Q078 — Readable in native Uliya text interface — UNKNOWN
- Finding: plain Markdown assumed readable; never rendered in Uliya UI.
- Evidence: absence (honest). Risk: low. Status: BLOCKED-NAS.

### Q079 — Users grasp "not a system recovery" — PASS
- Finding: stated in SKILL Goal, protocol, report §8 footer, README,
  PDF; asserted by tests.
- Evidence: `SKILL.md:8-10`, no-restored checks. Risk: low. Status: VERIFIED.

### Q080 — No excessive questions/jargon/output — PARTIAL
- Finding: zero clarification loops, bounded sections; label jargon remains
  (jury UV), mitigated by plain sentences.
- Evidence: jury-report TOPFIX4. Risk: low. Status: OPEN (minor).

## I. Maintainability, reproducibility and documentation

### Q081 — Repo understandable to newcomers — PASS
- Finding: README map + local-tests README + docstrings throughout.
- Evidence: `README.md:50-61`. Risk: low. Status: VERIFIED (review).

### Q082 — Every file necessary and documented — PASS
- Finding: all files listed with purpose; dev-kit + build outputs gitignored.
- Evidence: both READMEs, `.gitignore`. Risk: low. Status: VERIFIED (review).

### Q083 — Protocol and Skill consistent — PASS
- Finding: vocabulary guard test enforces heading-noun agreement with SKILL.md.
- Evidence: `run-tests.py` skill/report guard. Risk: low. Status: VERIFIED (test).

### Q084 — Generation deterministic — PASS
- Finding: 8/8 verdicts stable ×3 runs; reports regenerate byte-identically
  from same tree (timestamps: none embedded).
- Evidence: baseline repeatability column. Risk: low. Status: VERIFIED.

### Q085 — Dependencies pinned/documented — PARTIAL
- Finding: kit 0.7.3 + catalog 2.0.0 pinned; Python matrix 3.13/3.14;
  CI actions float on major tags; node 20 (deprecated upstream, still works).
- Evidence: `.github/workflows/ci.yml`. Risk: low.
- Improvement: pin action SHAs. Status: OPEN (minor).

### Q086 — Runs on Windows/Linux/macOS — PARTIAL
- Finding: windows + ubuntu CI green; macOS untested (no runner budget).
- Evidence: run 42400074403 (4 test jobs). Risk: low (stdlib-only).
- Status: OPEN (minor).

### Q087 — Generated artifacts stay fresh — PASS
- Finding: regenerate-on-run design; CI rebuilds everything from checkout.
- Evidence: P48, CI. Risk: low. Status: VERIFIED.

### Q088 — README distinguishes implemented/simulated/future — PASS
- Finding: Test status table + Limitations + "not tested yet" banner.
- Evidence: `README.md:104-144`. Risk: low. Status: VERIFIED (review).

### Q089 — ZIP rebuildable from clean checkout — PASS
- Finding: CI assembles + verifies package contents on every run.
- Evidence: `.github/workflows/ci.yml:44-61`. Risk: low. Status: VERIFIED.

### Q090 — Release checks auditable — PASS
- Finding: SHA256SUMS + checker evidence + content hashes + CI logs.
- Evidence: `A SOUMETTRE/SHA256SUMS.txt`, `evidence-index.md`.
- Risk: low. Status: VERIFIED.

## J. Innovation, commercial potential and judging

### Q091 — Urgent, payable problem — PARTIAL
- Finding: real post-disruption question; low frequency (jury UV 5→6).
- Evidence: jury-report, thesis §1/§5. Risk: medium. Status: OPEN (market).

### Q092 — Substantive differentiation vs UGREEN features — PARTIAL
- Finding: evidence labels + abstention + refusal-to-restore over stock
  find/QA/collect; thin but real.
- Evidence: baseline gap analysis. Risk: medium. Status: OPEN (needs NAS proof).

### Q093 — Distinct from Synology/QNAP/Veeam — PARTIAL
- Finding: documentary-dependency vs image/machine-level verification —
  different layer, documented with sources; no head-to-head run.
- Evidence: thesis §3 table. Risk: medium. Status: OPEN (needs pilot).

### Q094 — Semantic Recoverability demonstrated — PARTIAL
- Finding: label+reconcile+abstain demoed on 8 local cases; no semantic
  graph structure beyond the evidence table.
- Evidence: sample reports. Risk: medium. Status: OPEN, BLOCKED-NAS.

### Q095 — UGREEN integrable without redesign — PARTIAL
- Finding: pure Skill, zero platform changes needed; adoption value unproven.
- Evidence: `SKILL.md` (no new capabilities). Risk: low technically.
- Status: OPEN (commercial).

### Q096 — Measurable payable outcome — PARTIAL
- Finding: hypothesis defined (pre-flag rate saves failed-restore labor);
  unmeasured.
- Evidence: thesis §4/§11. Risk: medium. Status: OPEN (needs pilot).

### Q097 — Credible OEM/partnership strategy — PARTIAL
- Finding: thesis documents OEM path + pilot + license fit; no outreach made.
- Evidence: thesis §6/§11/§12. Risk: low. Status: OPEN (human authorization).

### Q098 — Defendable advantage beyond prompting — FAIL
- Finding: no hard moat today; orchestration over stock actions is copyable.
  Overclaiming would fail scrutiny; honesty is the position.
- Evidence: jury INN 4/10, thesis §10. Risk: low for hackathon (moat is
  not a judging criterion). Status: OPEN (future roadmap).

### Q099 — Judge gets it in 3 minutes — PARTIAL
- Finding: report + labels readable fast; proof presented is local-only,
  which costs persuasion.
- Evidence: jury-report. Risk: medium. Status: OPEN.

### Q100 — All major claims survive scrutiny — PARTIAL
- Finding: every local claim is evidence-backed; every NAS claim is
  explicitly withheld. Survives on honesty, fails on runtime proof —
  which Round 1 does not require.
- Evidence: this matrix + evidence index. Risk: medium. Status: OPEN, BLOCKED-NAS.

## Tally

- PASS: 40 (Q001–Q004, Q006–Q007, Q009–Q013, Q015, Q018–Q019, Q032, Q053,
  Q055, Q057–Q063, Q066–Q069, Q074, Q076–Q077, Q079, Q081–Q084, Q087–Q090)
- PARTIAL: 46 — mostly "local PASS, NAS UNKNOWN"
- FAIL: 2 (Q027 optional syntax, Q098 moat — both documented, neither blocking)
- UNKNOWN: 12 (all model/runtime behavior, honestly held)
- NOT APPLICABLE: 0
- Single biggest risk class: untested model behavior (E section + D high-risk
  halves) — addressable only with NAS access.
