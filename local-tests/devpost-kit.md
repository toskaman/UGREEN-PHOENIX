# Devpost draft kit (human pastes; nothing auto-submitted)

Status: DRAFTS for the user to paste into Devpost. No submission performed.
All claims match the verified repo state at HEAD.

## Title

PHOENIX — Recovery Intelligence for UGREEN AI NAS

## Tagline (elevator pitch)

Do your saved files actually let you resume? PHOENIX cross-checks project
prerequisites against NAS evidence and reports cited blockers — never a
fake "restored".

## Description (short)

PHOENIX is a Markdown-only Uliya Skill that assesses whether a project's
documentation and essential assets are sufficient to prepare its recovery
after a computer loss or team departure. It discovers project files inside
a user-authorized scope, extracts documented prerequisites, reconciles
cross-document version claims, verifies critical references, and assembles
a cited readiness report with five evidence labels
(FOUND / CONFLICTING / NOT FOUND IN SCOPE / INACCESSIBLE / UNKNOWN) and a
fail-closed verdict — including an honest INSUFFICIENT EVIDENCE abstention.
Report-only by default; saving requires a separate request plus platform
approval. Static checker: pass, 0 diagnostics. Local workflow logic: 59/59
checks, 14/14 mutation kills, 8/8 verdicts vs 6/8 for a strong retrieval
baseline. NAS runtime untested (no access in Round 1) — a 24-hour finalist
runbook is ready.

## Built With

`ug-filesystem`, `ug-document`, `ug-knowledge`, Uliya Skill Standard,
file-agent, document-agent, knowledge-agent, Markdown, Python (local
verification tooling only), GitHub Actions.

## Track

Open Innovation.

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
