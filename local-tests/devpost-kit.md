# Devpost draft kit (human pastes; nothing auto-submitted)

Status: DRAFTS for the user to paste into Devpost. No submission performed.
Pitch angle: Fail-Closed Evidence (tournament winner). All claims match the
verified repo state at HEAD; every number below matches the README test
table and the baseline report exactly.

## Title

PHOENIX — Recovery Intelligence for UGREEN AI NAS

## Tagline (elevator pitch)

Cited blockers or honest abstention — PHOENIX never fakes a restore.

## Description (short)

Every dependency gets one of five fixed evidence labels — FOUND,
CONFLICTING, NOT FOUND IN SCOPE, INACCESSIBLE, UNKNOWN — and every report
ends in a fail-closed verdict, including INSUFFICIENT EVIDENCE. Unlike file
search or generic QA that equate hits with health, PHOENIX reconciles
cross-document version claims, verifies exact paths, and refuses recovery
percentages and "restored" claims. Locally measured 8/8 verdicts with 2/2
abstentions and 22/22 citations vs 6/8 and 0/2 for a strong cited retrieval
baseline — NAS runtime honestly untested, finalist runbook ready.
Its Evidence Gain Planner names the single first verification per
blocker and states what observed result counts as resolved, then
Recovery Closure re-verifies after the user acts.

Yes: this is currently prompt orchestration over stock Uliya experts with
zero NAS execution traces — that is precisely why the product bet is
evidence discipline (labels, abstention, citations, access handling) rather
than rescue promises, and why NAS traces are the scheduled finalist proof.
Report-only by default; saving requires a separate request plus platform
approval. Static checker: pass, 0 diagnostics. Local workflow logic: 92/92
checks, 17/17 mutation kills. A Markdown-only Skill delegating to
registered file-agent, document-agent, and knowledge-agent experts; no
external APIs, no custom runtime code.

## Built With

`ug-filesystem`, `ug-document`, `ug-knowledge`, Uliya Skill Standard,
file-agent, document-agent, knowledge-agent, Markdown, Python (local
verification tooling only), GitHub Actions.

## Track

Open Innovation.

## Narrative hierarchy (v9.1 — all claims map to shipped behavior)

One-sentence pitch: PHOENIX tells you what to verify next to make a
disrupted project recoverable, and proves whether the blocker cleared.

30 seconds: Backed-up files do not mean a recoverable project.
PHOENIX checks your authorized NAS files against the project's own
documents, reports cited blockers, names the single first
verification, and re-verifies after you fix it — never claiming a
restore it did not test.

90 seconds: a studio loses its main machine; the NAS copy looks
complete. File search finds every name, so everyone assumes the
project is safe. PHOENIX reads the deployment guide, finds it
requires `config/prod-config.yaml`, verifies the exact path is
absent, and reports a documentary blocker with the proof. Its
planner says: first, supply that exact file; resolved if a scoped
check finds it. The operator adds the file; PHOENIX re-inspects
fresh evidence and appends a Recovery Delta: resolved — while
stating this is still not a tested restore.

Differentiation: chatbots match words; PHOENIX verifies exact paths,
arbitrates version conflicts against observed files, abstains on
denied or truncated sources, and re-observes after fixes (locally
8/8 with 0 false clears vs 1/8 with 5 for pasted-text QA).

## Try it out

- Repo: https://github.com/toskaman/UGREEN-PHOENIX
- Install: README Installation (5 steps, checker-gated).
- Local proof: `python local-tests/run-tests.py` (stdlib-only).

## Images (attach in this order)

1. `docs/architecture.svg` (orchestration flow — accurate, no mock UI).
2. Excerpt of `local-tests/reports/core-a.md` (§4 evidence table + §8 verdict).
3. Baseline table excerpt (6 methods, absolute counts).

## Video

Round 1: none required. Round 2 (if finalist): storyboard in
`local-tests/demo-script.md`; footage must come from the real NAS session.

## License / disclosures (paste into Devpost fields)

- License: PolyForm Strict 1.0.0 (noncommercial; commercial use needs a
  separate license). Same as author's OpenBridge project.
- AI assistance: OpenAI ChatGPT (GPT-6) for orchestration design/drafting;
  Muse Code (Meta Muse Spark) for verification tooling/packaging review.
- Third-party: UGREEN Uliya Skill Kit 0.7.3 + capability catalog 2.0.0
  (UGREEN terms apply); nothing else bundled.

## Pre-submit checklist

- [ ] Title, tagline, description pasted and re-read for overclaims.
- [ ] Built With tags set; track = Open Innovation.
- [ ] Repo link points at `main`; CI badge green on HEAD.
- [ ] PDF + ZIP from `A SOUMETTRE/` uploaded (current hashes in SHA256SUMS.txt).
- [ ] Images attached; no video claimed for Round 1.
- [ ] License + AI disclosures filled.
- [ ] Deadline: Nov 15, 2026, 11:45 PM PT.
