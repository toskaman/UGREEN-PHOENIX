# v9 Iota — first-place jury simulation (v8 baseline: 8.0)

Personas score the actual deliverables (PDF 456w, ZIP static-pass,
repo evidence). A score rises only on new relevant evidence.

## Judge 1 — Everyday NAS user (User Value)

- v8: 8. v9: **8 (HOLD)**.
- Evidence for: planner (FIRST CHECK + resolved-if + residual) makes
  the next action concrete; 12/12 criteria measured; proposal
  pitch rewritten for instant comprehension; usability package
  ready-to-run (fixtures, consent, analyzer all smoke-tested).
- Strongest objection: still zero observed users; comprehension
  proxy measures text, not humans.
- Missing proof: one real participant run (protocol ready).
- Next highest-value action: run the study (BLOCKED-HUMAN).

## Judge 2 — UGREEN platform engineer (Technical Quality)

- v8: 9. v9: **9 (HOLD)**.
- Evidence for: 92/92 + 147/147 + 39/39 + 20/20 + 15/15 + 17/17,
  consistency guard in CI, hardened builder (kit pin, recursive,
  limit asserts), E4 stale fix, E10 contract defense, renders match
  contract, ZIP static-pass 0/0.
- Strongest objection: all green is still offline; no NAS trace.
- Missing proof: Gate 2–3 green on hardware.
- Next highest-value action: finalist-day installation + smoke.

## Judge 3 — Innovation specialist (Innovation & Differentiation)

- v8: 7. v9: **8 (+1)**.
- Evidence for: Evidence Gain Planner is user-visible and
  evidence-selected (4 candidates, deterministic ablation 0/12 →
  12/12 criteria, verdicts identical, guarded transfer trials with
  honest mixed results). Verdict checklist is a transferable
  safety mechanism, not a prompt tweak. Falsifiable NAS-native
  proof (Gamma) with per-case falsifiers.
- Strongest objection: the planner is a report-format innovation;
  no live NAS demo of it yet.
- Missing proof: filmed §7 on hardware + one competitor failing it.
- Next highest-value action: demo video (BLOCKED-NAS).

## Judge 4 — Commercial evaluator (AI NAS Fit & Validation)

- v8: 8. v9: **9 (+1)**.
- Evidence for: Zeta found a REAL transfer bug (14B false clear on
  truncation) and fixed it with a verified checklist — validation
  catching bugs, not rubber-stamping. 14-rule transfer gate table
  names every hardware assumption + finalist test. Short
  instruction honestly rejected 0/4. Runbook gates + fallbacks +
  model-risk watch list.
- Strongest objection: proxies are not Uliya; fit unproven.
- Missing proof: Round 2 hardware runs.
- Next highest-value action: Gate 3 evidence on the NAS.

## Matrix

| Criterion | v8 | v9 | Evidence | Remaining gap |
|---|---|---|---|---|
| User Value | 8 | 8 | planner 12/12, study ready | zero users |
| Innovation | 7 | 8 | planner selected+measured | no live demo |
| Technical Quality | 9 | 9 | all suites + guards | no NAS trace |
| AI NAS Fit | 8 | 9 | transfer bug found+fixed | proxies ≠ Uliya |

Average 8.0 → **8.5**. Confidence: medium-high for Round 1;
no 10/10 is defensible before NAS access.

## Final verdict answers

1. Reject: "impressive offline rig, zero hardware proof, zero users."
2. Gold: "only entry that proves what it can't do — abstention,
   transfer gates, and bugs caught pre-NAS — while shipping a
   user-visible planner."
3. Better than a chatbot: exact-path verification, conflict
   arbitration, denial/truncation abstention, re-observation
   (8/8 vs 1/8, 0 vs 5 false clears, measured).
4. Most compelling innovation: "what to verify next, and what
   counts as proof" — the planner's FIRST CHECK + resolved-if.
5. Missing for 10/10: NAS traces, one user run, filmed demo.
6. Highest-impact action: finalist-day Gate 3 (real evidence loop).
