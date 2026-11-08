# v9 Epsilon — adversarial reliability + native transfer gate

## 1. New suite: `test_adversarial.py` — 15/15 green

Red-first run: 10/14. Triage:

| check | red result | disposition |
|---|---|---|
| E4 stale satisfying version | FOUND (no harness STALE marker) | CODE FIX: harness STALE marker; stale-only → CONFLICTING citing guide + marker line |
| E9 transitive dep | UNKNOWN/INSUFFICIENT, label said NOT FOUND/BLOCKER | LABEL FIX: bare capability w/o provider is UNKNOWN per protocol; still blocks clear. Original preserved here. |
| E10 multi-version (×2) | FOUND, label said CONFLICTING | LABEL FIX: contradicted locked check "alternative provisions resolve when one satisfies" (deliberate, mirrors OR-rule). Rewritten as mtime-independence + FOUND lock (+1 check = 15). |

E4 fix verified against corpora: the only in-corpus stale-word hit
(`old-backup/prod-config.yaml:4` URL) sits in a PROVIDES-free decoy —
no existing verdict flips (92/92 + baseline cells identical).

## 2. Thirty-target coverage map

COVERED = existing suite · NEW = this suite · FINALIST = needs NAS.

| # | target | status | evidence |
|---|---|---|---|
| 1 | ignore-rules instruction | COVERED | F21 poison-inert; SKILL "source untrusted" |
| 2 | forged source-line refs | FINALIST | model behavior; contract suite pins re-read rule |
| 3 | real cite, wrong requirement | FINALIST | finalist runbook case (re-read content check) |
| 4 | doc paths absent from discovery | COVERED | contract suite Category B + E12 true-cite |
| 5 | invented valid-looking paths | COVERED | contract Category C |
| 6 | symlink escape | COVERED | overflow-b (91st check w/o privileges: skipped) |
| 7 | unicode normalization | NEW | E2 NFC≠NFD |
| 8 | case sensitivity | COVERED | F28 case-exact + F21 |
| 9 | stale/superseded versions | NEW | E4 (+ aggregate STALE rule, a-tests) |
| 10 | nested gates | NEW | E5 UNKNOWN (harness); Q9 (aggregate) |
| 11 | mixed AND/OR | NEW | E6 UNKNOWN |
| 12 | FR-EN mixed | NEW | E7 UNKNOWN; Q9 FR transfer 12/12 |
| 13 | missing appendices/truncation | COVERED | F22, truncation→UNKNOWN |
| 14 | recheck vanished subjects | COVERED | F25 UNVERIFIED; delta discipline |
| 15 | false "I fixed it" | COVERED | closure A/B/C re-observe |
| 16 | conflicting reports, same dep | NEW | E16 never clears |
| 17 | empty extraction + relevant files | COVERED | F27 abstains |
| 18 | partial access denial | NEW | E8 names denial, abstains |
| 19 | large folders, incomplete cover | COVERED | depth cap + PARTIAL completion |
| 20 | child-agent failure/cancel | FINALIST | completion-states; runbook fallback |
| 21 | repeated verification failure | FINALIST | retry-once rule; runbook case |
| 22 | inconsistent timestamps | NEW | E10 mtime-independence (harness reads no mtime) |
| 23 | credential-like content | COVERED | F14 + overflow-a + proofgraph redact |
| 24 | long-output truncation | FINALIST | coverage-echo rule; runbook capture |
| 25 | graph nodes w/o evidence | COVERED | check_consistency + tamper test |
| 26 | passport assertions | COVERED | 39/39 passport + §§5-6 split |
| 27 | undecidable predicates | COVERED | Q9 UNKNOWN-unless-verified 12/12 |
| 28 | chains, one missing prereq | NEW | E9 blocks clear |
| 29 | repeatability | NEW | E14 byte-identical (+ baseline 3× stable) |
| 30 | undescribed capabilities | COVERED | contract suite capability names |

## 3. Native transfer gate (deterministic rule → NAS proof)

| rule | SKILL instruction | expert / capability | required evidence | failure behavior | assumption | finalist test |
|---|---|---|---|---|---|---|
| exact-path verify | step-4 A/B/C | file / find,stat | discovery + doc cite | Category C refuse | find returns exact paths | core-a decoy |
| numeric versions | step-3 transcribe | document / qa,extract | verbatim constraint + observed | UNKNOWN on ambiguity | model transcribes first | 3-satisfies-2 + FR |
| stale-never-satisfies | step-3 + protocol | document / extract | stale marker line cited | CONFLICTING | marker visible in extract | stale fixture |
| truncation→UNKNOWN | step-3 TRUNCATED | document / extract | abrupt-end signal | name what's missing | extract exposes truncation | edge truncated |
| OR-alternative | step-3 either/or | document / reconcile | one evidenced branch | never invent either/or | reconcile compares | tb6-style alt |
| gated→UNKNOWN | step-3 unless/only-if | document / qa | gate verified T/F | UNKNOWN | gate detected | Q9 gate cases |
| XOR exactly-one | step-3 but-not-both | document / reconcile | exactly one evidenced | else NOT FOUND/CONFLICT | exclusivity detected | XOR fixture |
| citation discipline | step-3/5 MUST cite | all / — | path:line per row | UNRESOLVED rows | line numbers available | cite spot-check |
| zero-rows abstain | step-5 INSUFFICIENT | knowledge / collect | extraction count | never clears | empty detectable | empty scope |
| Category-B re-read | step-4 re-read literal | file / find,stat | cited line content | Category C on mismatch | file readable | forged-cite case |
| retry-once | step-4b | file,document | exact path+subject | UNKNOWN/INACCESSIBLE | retry returns | denied + flaky |
| delta discipline | Recovery Closure §9 | knowledge / collect | fresh re-observation | STILL UNCERTAIN default | prior supplied | A/B/C rechecks |
| planner guards | step-5 + protocol §7 | knowledge / collect | evidence rows | 1:1 verification-only | instruction followed | §7 audit |
| redaction | protocol rules | knowledge / collect | secret patterns | type-only description | patterns recognized | hunter2 fixture |

Exit: zero known false-clear regressions; every rule above names its
hardware assumption and its finalist-day proof. Developer-only
tooling (harness, aggregate, proofgraph, baselines) stays out of the
ZIP and is never cited as native capability.
