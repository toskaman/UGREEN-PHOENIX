# Independent jury panel report (adversarial)

Method: 4 parallel judges (one criterion each) + synthesis agent, all
read-only, instructed to argue why PHOENIX does NOT deserve a high score.
Judged tree: commit `4faa985` (pre-Cycle-3; the panel ran before the
fixes). Scores are the judges' own, never inflated by the author.

## Panel scores (pre-Cycle-3 fixes)

| Criterion | Score | Confidence | One-line justification |
|---|---|---|---|
| User Value | 5/10 | medium | Clear workflow, honest citations; infrequent problem, jargon verdicts, zero NAS proof |
| Innovation & Differentiation | 4/10 | high | Clever evidence-label framing; zero novel AI, pure prompt orchestration of stock actions |
| Technical Quality | 6/10 | high | Disciplined local harness; core NAS/expert/approval behavior prompt-only, unexecuted |
| AI NAS Fit & Validation | 3/10 | high | Correct CLI mapping on paper; zero NAS runtime evidence, generic doc-QA fit |

Panel average: 4.5/10.

## Points of agreement (all/most judges)

- Zero real-NAS runtime evidence; 46/46 and 8/8 are local simulation.
- Local proof is regex-marker simulation, not AI measurement.
- Report-only, document-level only: restores nothing, next steps generic.
- Scope/read-only/approval enforcement is prompt prose, unexecuted on NAS.
- Portable chatbot-RAG shape; novelty is standard RAG hygiene.

## Splits

- Evidence labels + abstaining verdicts: clever/disciplined (INN/TECH) vs
  hurts comprehension (UV).
- Local rigor (46 checks then, traversal/mutation/CI) vs strawman
  baselines (INN; retrieval_plus already hit 6/8 + 5/5 blocker recall).
- Version-conflict design praised; truncation/symlink/heading risks
  flagged (TECH) — all three fixed in Cycle 3.

## TOPFIX disposition after Cycle 3

1. Real NAS evidence — OPEN, BLOCKED-NAS (runbook + rehearsal ready).
2. NAS-native or narrower claim — PARTIAL: claim already narrowed in
   README/SKILL; NAS-native semantics still unproven.
3. Concrete recovery value — PARTIAL: plain-language verdicts + per-label
   next steps shipped; still no remediation actions (out of scope).
4. Simplify UX — PARTIAL: plain-language sentences added; scope picker
   still manual, labels unchanged.
5. Harden + honest baselines — DONE locally: OS-error mapping, wider
   redaction, collision-proof versions, symlink consistency, drift guard,
   dead code removed, cited retrieval_plus with abstention rule, CI
   matrix 3.13+3.14 × ubuntu+windows. Skill-side guards remain prose.

## Post-Cycle-3 reassessment (author, evidence-backed)

| Criterion | Was | Now | Why |
|---|---|---|---|
| User Value | 5 | 6 | Plain-language verdicts directly answer the jargon charge; frequency/scope friction remain |
| Innovation | 4 | 4 | Unchanged: still prompt orchestration; honest baselines narrowed the measured gap |
| Technical Quality | 6 | 7 | Every concrete TECH finding fixed + regression-tested; NAS behavior still unexecuted |
| AI NAS Fit | 3 | 3 | Unchanged: zero runtime evidence by construction of Round 1 |

Reassessed average: 5.0/10 (medium confidence).

## Strongest remaining objection

A prompt-only portable doc-QA report with zero NAS execution that
catalogs what documents say but restores nothing — why is this a NAS
skill rather than generic RAG any competitor copies in hours? The only
honest answers: the evidence discipline (labels, abstention, citations,
access handling) is the product bet, and NAS execution is the scheduled
proof. Until finalist-day traces exist, the objection stands.

---

# v4 re-evaluation (adversarial, post-Recovery-Closure)

Method: same adversarial posture, applied to the v4 tree by the author
acting as skeptical judge. Judged per Round 1 rules: absence of NAS
runtime evidence must not itself reduce the score — design fit,
credibility, and validation plan are judged instead. Every score needs
evidence, a remaining objection, and what would raise it.

## User Value: 6 -> 7

Evidence: Recovery Closure answers the exact question report-only QA
left users alone with — "did my fix actually work?" — via enforced
re-inspection and a Recovery Delta with per-finding states (RESOLVED /
STILL BLOCKED / NEW BLOCKER / ...). P1-before-P2 recommendations give
next actions; the "What you get" block explains blockers in plain
English; flagship A/B/C demonstrates before/after on three distinct
failure shapes.
Strongest remaining objection: still document-level (restores nothing),
and the user-study protocol has zero participants — usability is
designed, not observed.
Higher needs: real user-study data (protocol + fixtures ready) and
finalist-day UX traces.

## Innovation & Differentiation: 4 -> 6

Evidence: Recovery Closure is a genuine workflow innovation inside
Skill constraints — recheck-via-user-supplied-prior-report plus
delta-compare works without platform persistence, which no
report-only QA offers. Track A/B split plus published two-model
transcripts is evaluation honesty competitors rarely show.
Strongest remaining objection: still prompt orchestration over stock
catalog actions; no novel AI, no NAS-only mechanism proven.
Higher needs: a demonstrated capability that collapses without NAS
tool access (finalist-day ablation), or a defensible reasoning asset.

## Technical Quality: 7 -> 8

Evidence: 71/71 checks, 16/16 mutation kills including delta mutants,
stable 8/8 vs 6/8 vs 3/8 vs 1/8 baseline, two-model Track B with
committed transcripts and strict rubric grading (9B 3/6, 14B 3/6,
corrected same-day after a grading-frame error — see results.md),
a real runner bug found and fixed during grading (last-match verdict
parsing), CI with pinned actions, kit checksum, and macOS coverage.
Strongest remaining objection: the Skill's core (delegation, approval,
truncation) is still prompt prose until NAS execution.
Higher needs: finalist-day traces confirming delegation + approval
behavior.

## AI NAS Fit & Validation: 3 -> 5

Evidence: the assistant-vs-PHOENIX comparison grounds the NAS-native
claim in mechanism, not marketing — existence verification, metadata,
cross-document reconciliation, and the re-inspection loop are
meaningless with pasted text alone. Validation plan is concrete:
8 corpora, Core A–E runbook, rehearsal green, Track B local inference
disclosed as non-NAS.
Strongest remaining objection: zero NAS runtime evidence by
construction; the fit argument is designed, not demonstrated.
Higher needs: finalist-day execution traces (the scheduled proof).

Reassessed v4 average: 6.5/10 (medium confidence), up from 5.0.
The +1.5 comes from a real workflow (Closure), real inference data
(Track B), and a mechanistic NAS-fit argument — not from re-grading
the same artifact.

---

# v5 re-evaluation (adversarial, post-reliability program)

Same posture. New evidence since v4: TB3/TB5/TB6 root-caused and fixed
on local models; single-shot rule-interference demonstrated with two
refuted hypotheses; Arch B pipeline (extract → verify → escalate →
deterministic aggregate) scores 28/28 on Track B + dev + validation
and 9/10 on the locked set with zero false clears; 9B transfer 5/6
with zero context burns; Vultr harness built but BLOCKED-CREDENTIALS
($0 spent); reasoning procedures transferred into the Skill; recheck
shown claim-proof under separation and claim-vulnerable single-shot.

## User Value: 7 -> 8

Evidence: the recheck loop now has measured reliability behind it
(28/28 + locked 9/10, errors fail safe-side), Proof Graph and Passport
designs make reports portable and auditable, and the false-fix-claim
rejection (c2/x30) answers "did my fix work" with evidence instead of
trust.
Strongest remaining objection: still no real user observed; value is
measured on synthetic tasks, not human outcomes.
Higher needs: user-study runs + NAS UX traces.

## Innovation & Differentiation: 6 -> 7

Evidence: Arch B separation (transcribe-then-judge with deterministic
nets) is a genuine reliability architecture, not a prompt tweak; the
verify/escalate loop and grounded-ALT/truncation-net mechanisms are
novel within the Skill-constrained design space; single-shot
claim-vulnerability vs separated claim-proof is a demonstrated,
honest negative result competitors don't publish.
Strongest remaining objection: orchestration + procedures, still no
proprietary model or NAS-only mechanism proven.
Higher needs: NAS-execution ablation proving the loop collapses
without tool access.

## Technical Quality: 8 -> 9

Evidence: 30-case split benchmark (dev/validation/locked) with frozen
labels; 30 offline aggregation tests + 20 harness tests, all green;
locked discipline honored (x26 French-gap recorded, not patched);
transcript-committed grading; systematic-debug + verification gates
followed with same-day corrections disclosed; CI green on 3 OS × 2
Python with kit checksum.
Strongest remaining objection: core delegation still unexecuted on NAS.
Higher needs: finalist-day traces.

## AI NAS Fit & Validation: 5 -> 6

Evidence: validation program is now the strongest in the repo's
history (38 held-out cases, two models, locked eval, zero false
clears); the transfer section in the Skill states exactly what was
validated locally vs what needs NAS confirmation; Vultr campaign is
staged (not run) with budget/identity controls pre-verified.
Strongest remaining objection: fit remains designed, and the Vultr
diversity leg never executed for lack of a key.
Higher needs: NAS traces, or Vultr runs once keyed.

Reassessed v5 average: 7.5/10 (medium confidence), up from 6.5.
The +1.0 comes from measured reliability (28/28 + locked 9/10), a
transferred reasoning upgrade in the Skill itself, and honest
boundaries (locked discipline, blocked Vultr, documented residuals).

---

# v6 re-evaluation (adversarial, post-native-transfer + red-team)

Same posture, Round 1 rules (no penalty for absent NAS runtime; design
fit, credibility, validation plan judged instead). New evidence since
v5: X26 closed (locked rescore 10/10, original 9/10 preserved) via an
EN/FR constraint normalizer (41 probes, m01-m12 12/12 on 14B);
red-team found and fixed 4 false-clear-class defects (negation
exclusions, plural chains, NFKC "!=" fold, gap->FOUND mislabel),
purple-verified with no regressions (contract now 122 checks, 86/86
acceptance, 16/16 mutation); Proof Graph + Passport graduated from
design to tested implementation (37 checks, rendered before/after
artifacts); reservation ledger + harness F11-F26; Skill reliability
rules transferred with a native-transfer report (9 mappings, 10
numbered unverified assumptions, 10 mapped finalist tests);
checker static-pass on the new content. Still missing: any NAS trace,
any Vultr run (BLOCKED-CREDENTIALS, $0), any user-study participant,
9B tb6 residual OPEN.

## User Value: 8 -> 8 (hold)

Evidence: rendered Passport/Delta artifacts make the Closure loop
concrete and auditable; scenario-A before/after is now generated, not
described. Against: zero observed users, unchanged; frequency/scope
friction unchanged.
Strongest remaining objection: value is measured on synthetic tasks,
not human outcomes.
Higher needs: user-study runs + NAS UX traces.

## Innovation & Differentiation: 7 -> 7 (hold)

Evidence: the normalizer (deterministic EN/FR constraint semantics
with fail-closed proofs) is the first defensible reasoning asset in
the repo; exclusion/chain/unicode handling has no prompt-tweak
equivalent. Against: still orchestration + procedures, no NAS-only
mechanism demonstrated; no new capability class since Closure.
Strongest remaining objection: a strong engineering program around a
v4-shaped product, not a second breakthrough.
Higher needs: NAS-execution ablation proving the loop collapses
without tool access.

## Technical Quality: 9 -> 9 (hold)

Evidence: red/purple cycle with before/after proof on real defects
(including one regression the purple pass caught in the red fix
itself); 122 + 86 + 37 + 31 + 35 offline checks green; rendered
artifacts byte-reproducible; checker static-pass.
Strongest remaining objection: the Skill core (delegation, approval,
native-model behavior) is still unexecuted prose on the target.
Higher needs: finalist-day traces. 10/10 explicitly not claimed.

## AI NAS Fit & Validation: 6 -> 7

Evidence: the native-transfer report is exactly what Round 1 can
judge — each local reliability rule mapped to a Skill instruction,
an expert/capability, an expected behavior, and a numbered
assumption, with 10 finalist tests closing the loop; the Skill now
encodes citation/disagree/truncation/allowlist/retry/delta rules
instead of describing them in prose docs.
Strongest remaining objection: fit is still designed; every T-row is
a prediction until the NAS runs.
Higher needs: NAS traces (tests T1-T9 are staged and ready).

Reassessed v6 average: 7.75/10 (medium confidence), up from 7.5.
The +0.25 comes from one justified move (Fit 6->7: transfer made
auditable) plus held scores on a strictly stronger evidence base.
Three holds are deliberate: without NAS traces, users, or a second
product breakthrough, higher would be grade inflation.

---

# v7 re-evaluation (adversarial, post-allowlist fix + conditionals)

Same posture, Round 1 rules. New evidence since v6: a CONFIRMED
contradiction in the shipped Skill was found and fixed — v6 step-4
"refuse any path the discovery did not verify" forbade exactly the
check the flagship missing-dependency scenario requires; it is
replaced by a Category A/B/C contract (discovered + document-cited
paths checked in-scope, invented paths refused, traversal/out-of-scope
rejected), pinned by a new 12-check skill-contract suite, mirrored in
the protocol, with transfer T4/U5/test5 corrected and checker
static-pass. Second: conditional-dependency semantics — the XOR
anti-pattern (members rejected AND non-members cleared) fixed with
exactly-one compare, unless/only-if/si gates abstain instead of
silently clearing, 13 new contract checks (135 total, zero v6
regressions), injection red-team probes abstain, native transfer via
protocol rules + in-context step-3 sentence + T10/U11. Third: demo
script gained the Recovery Closure beat (fix → recheck → Delta);
stale counts corrected (85→86, 122→135, unverifiable 41/41 probe row
removed). Still missing: any NAS trace, any Vultr run
(BLOCKED-CREDENTIALS, $0), any user-study participant, 9B tb6
residual OPEN, no local-model conditional run (new U11).

## User Value: 8 -> 8 (hold)

Evidence: the flagship scenario is now executable as written (v6
Skill forbade its own core check); conditional handling removes a
class of silent misreads users would have met as wrong verdicts.
Against: zero observed users, unchanged; value still measured on
synthetic tasks.
Strongest remaining objection: designed value, not observed outcomes.
Higher needs: user-study runs + NAS UX traces.

## Innovation & Differentiation: 7 -> 7 (hold)

Evidence: the A/B/C scope-preserving verification contract is a real
design contribution under Skill constraints, and gated/XOR semantics
extend the reasoning asset to ordinary real-world requirement shapes.
Against: both are correctness + coverage on the v4-shaped product —
a contradiction fix and an asset extension, not a second breakthrough
or a demonstrated NAS-only mechanism.
Strongest remaining objection: the product does nothing a user can
see that v6 did not promise; it now keeps the promise.
Higher needs: NAS-execution ablation proving the loop collapses
without tool access.

## Technical Quality: 9 -> 9 (hold)

Evidence: TDD discipline held (contract suites RED-before-GREEN),
red/purple cycle on conditionals with tangled-input pins, injection
probes abstain, 135 + 86 + 37 + 31 + 35 + 12 checks green, rendered
demo byte-reproducible, checker static-pass on new content.
Strongest remaining objection: native core still unexecuted on target.
Higher needs: finalist-day traces. 10/10 explicitly not claimed.

## AI NAS Fit & Validation: 7 -> 7 (hold)

Evidence: T10/U11 extend the auditable transfer; Category-B finalist
test stages the highest-risk native check; in-context rules reduce
reliance on linked-protocol recall.
Strongest remaining objection: still more predictions — every T-row
awaits the NAS, and U11 adds a fresh unverified assumption.
Higher needs: NAS traces (tests T1-T10 staged and ready).

Reassessed v7 average: 7.75/10 (medium-high confidence), unchanged
from v6. Four holds are deliberate: v7 is the most important
correctness release since v4 (the shipped Skill contradicted its own
flagship scenario), but correctness recovered is not a new
breakthrough, and Round 1 ceilings without NAS traces or users hold
firm. The confidence upgrade (medium → medium-high) reflects a
strictly stronger, contradiction-free evidence base.
