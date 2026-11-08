# Native transfer report — Cycle 2 (TITAN v6)

Source tree: `835c6e7` + Cycle 2 working-tree Skill edits (uncommitted at
writing time). Checker: official kit 0.7.3 `static-pass`, 0 errors, 0 warnings.

## 1. What "transfer" means

The local Python pipeline (extract / verify / escalate / aggregate) does NOT
run on the NAS. Transfer here means: each reliability rule that was proven
locally is restated as a short instruction inside the Uliya Skill contract
(`SKILL.md` + `references/decision-protocol.md`), using only officially
supported delegation to `file-agent`, `document-agent`, `knowledge-agent`.

An instruction-level transfer is NOT equivalent to hardware validation.
Section 7 lists every unverified platform assumption. Section 8 lists the
finalist tests required to close them. Actual Uliya behavior observed: NONE
(BLOCKED-NAS).

## 2. Locally proven deterministic behavior

Re-verified this session (offline, no credentials):

| Component | File | Checks | Result |
|---|---|---|---|
| Acceptance harness | `local-tests/run-tests.py` | 92 | 92/92 ALL GREEN |
| Mutation | `local-tests/mutate.py` | 17 | 17/17 killed |
| AI-lab harness | `ai-lab/tests/test_harness.py` | 31 | 31/31 |
| Budget ledger | `ai-lab/tests/test_budget.py` | 35 | 35/35 |
| Aggregation | `ai-lab/tests/test_aggregate.py` | 147 | 147/147 |
| Proof graph | `local-tests/test_proofgraph.py` | 39 | 39/39 |
| Skill contract | `local-tests/test_skill_contract.py` | 20 | 20/20 |
| Adversarial combinations | `local-tests/test_adversarial.py` | 15 | 15/15 |
| Wave-1 rehearsal | `local-tests/rehearse-wave1.py` | 8 prompts / 8 corpora | all passed |

Rules proven by these suites: suspect-row UNKNOWN; citation-gated verdicts;
delta path-anchoring with vanish-always-UNCERTAIN; verified-append rowfix
merge; TRUNC byte-confirmation; reservation ledger lifecycle; EN/FR
constraint semantics with fail-closed UNKNOWN; stale-never-satisfies.

## 3. Locally measured model behavior (Cycle 1 + v5, local Ollama)

Evidence: `local-tests/track-b/transcripts/`,
`local-tests/ai-lab/reports/transcripts/`, `track-b/results.md`.

| Model | Suite | Score |
|---|---|---|
| 14B qwen2.5-coder | Track B v3 | 6/6 |
| 14B | dev x01-x10 (arch-b) | 10/10 |
| 14B | val x11-x20 (arch-b) | 10/10 |
| 14B | closure c1-c2 | 2/2 |
| 14B | multilingual m01-m12 (arch-b) | 12/12 |
| 14B | locked x21-x30 rescore | 10/10 (x26 closed; original 9/10 preserved) |
| 9B qwythos | Track B | 5/6 (tb6 recall residual OPEN) |

These are local-model measurements, NOT Uliya predictions. The native NAS
model is unknown (size, tuning, context).

## 4. Transfer mapping (v6 §3.1)

Each row: local rule → Skill instruction → Uliya expert → expected behavior
→ unverified assumption (Un = §7 id).

| # | Local rule (proven) | SKILL.md | Protocol | Expert / capability | Expected on Uliya | Un |
|---|---|---|---|---|---|---|
| T1 | Citation gate: uncited rows are UNRESOLVED, support nothing (`aggregate`) | L41: every requirement MUST carry path:line citation | Citation discipline | document-agent / extraction | Each requirement row carries SOURCE-PATH + LOCATION | U1, U2 |
| T2 | Disagreement preserved, never silently resolved (`aggregate`) | L41: SUBJECT,CLAIM-A,SOURCE-A,CLAIM-B,SOURCE-B,AGREE\|DISAGREE | Conflict rule | document-agent / reconciliation | DISAGREE rows keep both sources | U2, U3 |
| T3 | TRUNC byte-confirmed → UNKNOWN (`aggregate`, tb5) | L41: TRUNCATED in LOCATION, name what is missing | Truncation rule | document-agent / extraction | Truncated docs flagged, requirements UNKNOWN | U4 |
| T4 | Check-then-report-absence: discovered (A) + document-cited (B) paths verified in-scope; invented (C) refused (`harness` safe_join+exists; v7 fix — the v6 refuse-if-undiscovered wording contradicted Core test A and was removed) | L43: Category A/B allowed, C refused, traversal/out-of-scope rejected | Verification sources | file-agent / discovery + metadata | PRESENT/ABSENT for A+B; OUT OF SCOPE/UNSAFE rejections | U5 |
| T5 | Verified-append rowfix: re-verify, never substitute (`aggregate` x14) | L44: ONE targeted retry per item, then label and proceed | Recheck rule | parent + responsible expert | Single retry, then UNKNOWN/INACCESSIBLE, no loops | U6 |
| T6 | Empty extraction never clears (gate requires resolved cite) | L46: zero cited rows → INSUFFICIENT EVIDENCE | Citation discipline | knowledge-agent / report assembly | INSUFFICIENT verdict on empty extraction | U7 |
| T7 | Coverage echo verbatim (no invented counts) | L46 + L55: echo coverage/failures verbatim | Evidence fidelity | parent presentation | Counts match expert-observed values | U7 |
| T8 | Delta: vanished subject is STILL UNCERTAIN (`delta`) | L51: prior subjects re-observed; absent → STILL UNCERTAIN | Delta discipline | parent / Recovery Delta | Delta marks un-re-examined subjects UNCERTAIN | U8 |
| T9 | EN/FR numeric version compare (`normalize`, 135-check contract) | L41: compare numerically (3 satisfies 2-or-newer) | Multilingual version rule | document-agent / extraction | Correct min/max/range/strict handling EN+FR | U2, U9 |
| T10 | Gated requirements abstain unless the gate is verified; XOR means exactly one (`normalize`, 135-check contract, v7) | via protocol: UNKNOWN gates, exactly-one exclusivity | Gated-requirements + exclusive-alternatives rules | document-agent / extraction + knowledge-agent / verdict | Gated rows UNKNOWN without verified gate; XOR rows satisfied by exactly one member | U2, U11 |

Published capabilities used: file discovery + metadata, document QA /
extraction / reconciliation, report assembly, approval-gated save. No custom
code, no remote calls, no new experts.

## 5. Deliberately NOT transferred (developer-only tooling)

Reservation ledger (`budget.py`), providers (`vultr.py`, `ollama.py`),
paid path (`call.paid_chat`), bench/escalate/smoke runners, corpora and
transcripts stay outside the Skill ZIP. They are research infrastructure;
the Skill must not depend on them. Verified: CI package-contents check
allows only `SKILL.md` + `references/*.md`.

v7 decision (Phase 7 investigation): no separate ASCII Proof-Graph
section was added to the native report. Every graph edge field
(requirement, source, status, version, uncertainty) is already carried
by the mandatory Evidence table, and every passport field (scope,
coverage, blockers, recheck history) by sections 1–9; a duplicated
graph view would lengthen the prompt and risk small-model drift for
no new evidence. The local `proofgraph.py` renderer stays the
reference visualization for the same verified rows.

## 6. Actual behavior observed on Uliya

NONE. No NAS access at writing time. All §4 "expected" cells are
predictions from local-model behavior, not observations.

## 7. Unverified platform assumptions

- U1: document-agent returns path:line-granular source locations.
- U2: the native model follows MUST-format output contracts on long docs
  (local 9B needed structural help on TB2; native size unknown).
- U3: reconciliation output preserves both conflicting claims verbatim.
- U4: extraction exposes truncation signals (cut sentences, missing pages).
- U5: file-agent performs a bounded in-scope existence check for a
  document-cited path (Category B), not only for discovery-listed
  paths; discovery results still pass verbatim to step-4.
- U6: the parent performs exactly one retry (instruction-following, no
  platform loop guard assumed).
- U7: knowledge-agent / parent do not summarize away explicit counts or
  reintroduce a verdict over INSUFFICIENT EVIDENCE.
- U8: prior-report context (pasted or authorized-scope file) is available
  at recheck time; no cross-conversation persistence is assumed.
- U9: native model handles French constraints per the protocol rule
  (locally proven only in Python + 14B pipeline, m01-m12 12/12).
- U10: `delegate` parameter syntax and expert availability on the real
  NAS firmware (open question for UGREEN).
- U11: native model applies gated-requirement abstention and XOR
  exactly-one per the protocol rules (locally proven only in Python;
  no local-model conditional run yet).

## 8. Required finalist tests (map to `finalist-runbook.md`)

1. Install Skill, confirm experts respond (runbook §1-2) → closes U10.
2. Run flagship scenario A/B/C corpora; check citation lines (T1) → U1, U2.
3. Feed conflicting docs; require DISAGREE with both sources (T2) → U3.
4. Feed truncated guide; require TRUNCATED + UNKNOWN (T3) → U4.
5. Request verification of (a) a document-cited but undiscovered path → bounded PRESENT/ABSENT check allowed, (b) an uncited invented path → refusal (T4) → U5.
6. Force UNRESOLVED once; count retries = 1 (T5) → U6.
7. Empty-scope run; require INSUFFICIENT, no verdict (T6) → U7.
8. Fix one blocker, recheck; require STILL UNCERTAIN for subjects the
   recheck did not re-examine (T8) → U8.
9. French-constraint case (x26-class, fresh wording); require correct
   numeric verdict (T9) → U9.
10. Gated case ("required unless B", fresh wording) → UNKNOWN without a
    verified gate; XOR case ("A or B but not both") → exactly-one
    verdict (T10) → U11.
11. Record latency, context behavior, approval flow; capture evidence.

## 9. Honesty ledger

- Static checker result: PASS (format/capability conformance only).
- Behavioral transfer: PREDICTED, not observed.
- Local model scores (§3) must never be quoted as NAS Skill accuracy.
- Original locked 9/10 (x26 fail) stands alongside the 10/10 rescore.
- 9B tb6 residual: OPEN — small-model risk for native deployment.
- v8 Q6: ai-lab citation checks stay range-only (path exists + line
  in range). Measured on all committed archb transcripts: a naive
  subject-in-cited-line rule would drop 44/128 rows (34%),
  including legitimate paraphrase citations (e.g. tb6 BACKUP →
  guide.md:3 "back the database up"). Wiring it into the scorer
  post-hoc would invalidate the published 28/28 + locked scores,
  so content-grounding stays limited to ALT lines (byte-verified)
  and to the native Skill's Category-B rule (literal path string
  must appear in the re-read cited line — appropriate because a
  path is a literal, not a paraphrase). Scorer-side content
  checks: OPEN, research-tooling only, no user-facing impact.
