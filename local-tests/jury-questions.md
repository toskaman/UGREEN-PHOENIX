# 50 hardest jury questions (with evidence-backed answers)

Source for Devpost FAQ and wave-1 prep. Every answer cites real evidence
or states the gap honestly. No invented metrics, users, or revenue.

## Problem and value (J01–J05)

**J01. Who feels this pain, concretely?** Small studios/teams resuming a
project after workstation loss or staff departure (README usage scenario).

**J02. How often?** Infrequent, high-stakes — admitted weakness (jury UV 6).

**J03. Why isn't backup enough?** Backups prove bytes copied, not that
project prerequisites are jointly satisfiable (thesis §3 table).

**J04. What does the user get?** A cited report: blockers, uncertainties,
next checks, plain-language verdict (sample `reports/core-a.md`).

**J05. Faster than manual search?** Unmeasured with users — honest gap;
locally, exact-path+version checks beat basename search 8/8 vs 3/8.

## Novelty (J06–J13)

**J06. What's new vs a RAG chatbot?** Fixed evidence labels, fail-closed
verdict ordering, mandatory abstention, access discipline (decision-protocol).

**J07. Can't anyone copy this in hours?** The prompts, yes — admitted
(INN 4). The moat would be measured verdict quality + OEM integration.

**J08. What does reconciliation add, measured?** Ablation: without it 6/8
and conflict detection drops 3/3 → 1/3 (baseline table).

**J09. What does verification add?** Without it 6/8 with 1 false clear
(stale decoy accepted) — ablation proves the stage.

**J10. Is abstention novel?** No — standard RAG hygiene, executed
disciplinarily (2/2 abstention cases, 0 forced verdicts).

**J11. Nearest competitor?** DocDrift (hackathon doc-reconcile skill):
differs by recovery verdicts + abstention + access handling (thesis §10).

**J12. Vs Veeam/Synology?** Different layer: documentary prerequisites vs
machine/image boot verification (thesis §3, sourced).

**J13. Memorable demo moment?** Stale decoy rejected: same filename, wrong
path → still flagged missing. Understandable in seconds.

## Technical (J14–J25)

**J14. Uliya-compliant?** Yes: checker `static-pass`, 0 diagnostics on
exact bytes; 3 registered experts, 9 catalogued actions.

**J15. Which capabilities, when?** ug-filesystem (discover/verify),
ug-document (extract/reconcile), ug-knowledge (report/save) — SKILL steps 2–5.

**J16. Scope safety on NAS?** Prose-enforced + scoped delegations;
platform enforcement UNVERIFIED (Q031 PARTIAL, runbook probes it).

**J17. Prompt injection?** Local corpus ignored; MODEL resistance untested
— top scheduled finalist test (runbook W1-G).

**J18. Secrets in reports?** 6 keyword classes + 3 token prefixes redacted,
tested; novel shapes = residual risk (Q036).

**J19. Fabricated citations?** Impossible locally (constructed paths);
model fabrication untested (Q037).

**J20. Denied vs missing?** Distinct labels INACCESSIBLE vs NOT FOUND,
tested (edge-3); NAS timeout signaling unknown (support Q4).

**J21. Approval bypass?** No save path executes without approval prose
gate; real gate behavior untested (Q035).

**J22. Version edge cases?** Total-order compare, never raises, long
versions collision-proof (unit-tested incl. nasty list).

**J23. Symlink escape?** Never followed; live-tested incl. no_verify-leak
assertion (Q032 PASS).

**J24. Deterministic?** 8/8 stable ×3 runs; reports regenerate
byte-identically (Q084).

**J25. Why no percentages?** File counts ≠ recovery; percentages would
mislead — explicit anti-rule (protocol).

## NAS fit and validation (J26–J33)

**J26. Why a NAS Skill, not a chatbot?** Runs where project files live,
inside user-authorized scopes, over NAS-native experts (SKILL delegations).

**J27. What runs on-device?** Unknown — Skill calls no external APIs, but
residency depends on UGREEN deployment; third-party evidence is mixed
(thesis §8). No on-device claim made.

**J28. Which NAS permissions matter?** Read scope + optional save approval;
real behavior is finalist-day test #6 (runbook).

**J29. What if experts truncate results?** PARTIAL completion + INSUFFICIENT
verdict by design; real truncation semantics unknown (support Q3).

**J30. Latency on large scopes?** NOT MEASURED on NAS; locally 13.4 ms at
43 files (explicitly not NAS latency).

**J31. Repeatability on NAS?** Unmeasured; deterministic layers stable 8/8.

**J32. Languages?** Platform reportedly EN/DE/ZH/JA (unverified); Skill adds
nothing language-specific.

**J33. What breaks first on NAS?** Top risks: injection discipline,
citation fidelity, scope enforcement — all scheduled day-one probes.

## Evidence and honesty (J34–J40)

**J34. What is actually proven?** Workflow logic on 8 synthetic cases +
static compliance. Everything else is labeled PARTIAL/UNKNOWN.

**J35. Why trust the baselines?** Predeclared labels, absolute counts,
strong cited comparator (retrieval_plus 6/8), ablations isolating stages.

**J36. Strawman baselines?** filename/generic_QA are weak by design (floor
estimators); the honest comparator is retrieval_plus — gap is exactly the
access+abstention discipline.

**J37. Mutation gaming?** 14 mutants incl. double + baselines mutant, each
killed by its intended check; CI enforces 14/14.

**J38. Cherry-picked corpora?** 8 fixed cases incl. healthy (must-clear) and
abstain (must-not-force) — both directions tested.

**J39. What was deliberately NOT claimed?** On-device, restore capability,
user speedups, revenue, buyer interest — all withheld (audit UNKNOWNs).

**J40. Biggest known weakness?** Zero model runs; every AI-quality question
is honestly UNKNOWN (E section).

## Commercial (J41–J45)

**J41. Who pays?** SMB studios/teams, per-NAS add-on or OEM bundle (thesis §6).

**J42. Why would UGREEN care?** Sticky native AI workload showcasing UGOS +
privacy story; zero platform redesign (thesis §2).

**J43. Defensibility?** None today — admitted FAIL (Q098); data + OEM depth
would build it.

**J44. Pilot?** 10 studios × 4 weeks, pre-flag precision ≥ 0.8 go/no-go
(thesis §11). Not run.

**J45. License fit?** PolyForm Strict blocks unlicensed commercial use —
consistent with an OEM deal requiring a commercial license.

## Demo and submission (J46–J50)

**J46. What will judges see Round 1?** PDF proposal + Skill ZIP + public repo
with CI green — no video required.

**J47. Reproducible?** Yes: stdlib-only suite, pinned CI matrix, byte-identical
ZIP rebuilds, content-hash index.

**J48. What's in the ZIP?** Exactly SKILL.md + 3 references (7.4 KB);
checker-verified, per-file hashes in SHA256SUMS.

**J49. If selected?** 24h runbook: smoke → env confirm → 8 scenarios →
approval test → regression + footage (finalist-runbook.md).

**J50. Why deserve to win?** Strongest honest entry: real compliance, real
local rigor, real adversarial review, zero fabricated proof — and a clear
plan to convert finalist access into NAS evidence.
