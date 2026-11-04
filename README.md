# PHOENIX — Recovery Intelligence for UGREEN AI NAS

> **UGREEN AI NAS Hackathon 2026 — Open Innovation — Round 1 submission**
> Status: static checker passed with zero diagnostics · real NAS runtime **not tested yet**.

PHOENIX assesses whether a project's documentation and essential assets are
sufficient to prepare its recovery after a computer loss or a team departure.
It identifies missing and conflicting dependencies with source-backed evidence —
and never confuses documentary readiness with a verified restoration.

## How it works

PHOENIX is a Markdown-only Uliya Skill. The parent orchestrates three
registered expert agents; it never executes NAS commands directly:

1. **file-agent** (`ug-filesystem`) — discovers project entry points, guides,
   manifests, and referenced files inside the user-authorized NAS scope only.
2. **document-agent** (`ug-document`) — extracts prerequisites, dependencies,
   and version constraints, then reconciles cross-document claims.
3. **knowledge-agent** (`ug-knowledge`) — assembles the evidence-qualified
   recovery-readiness report with citations, blockers, and next checks.

Every dependency is labeled `FOUND`, `CONFLICTING`, `NOT FOUND IN SCOPE`,
`INACCESSIBLE`, or `UNKNOWN`. The verdict is one of
`DOCUMENTARY BLOCKER IDENTIFIED`, `NO DOCUMENTARY BLOCKER FOUND IN REVIEWED
SOURCES`, or `INSUFFICIENT EVIDENCE` — never a recovery percentage, never a
"restored" claim.

## Why PHOENIX fits this hackathon

Mapped to the official judging criteria:

- **Usefulness** — answers a real question small teams ask after any
  disruption: "do our saved files actually let us resume?" with a cited,
  actionable report.
- **AI NAS Fit** — built for on-device private AI: every check runs inside a
  user-authorized NAS scope through `ug-filesystem`, `ug-document`, and
  `ug-knowledge`; no external APIs, no data leaves the NAS.
- **Creativity** — reframes recovery as documentary evidence: fixed evidence
  labels, abstention on incomplete data, and an explicit refusal to confuse
  "files found" with "restored".
- **Technical Execution** — `static-pass` (0 errors, 0 warnings) on the
  official checker, 31/31 local workflow-logic checks, a measured baseline
  comparison, and a validation plan ready for the NAS test day.

## Repository contents

| Path | Description |
|---|---|
| `SKILL.md` | The Skill: goal, required input, capability evidence, workflow, completion/failure rules |
| `references/decision-protocol.md` | Evidence states, output contract, anti-misleading rules |
| `references/validation-plan.md` | Planned tests (missing artifact, incompatible version, hostile evidence) |
| `references/disclosures.md` | Authorship, AI assistance, third-party and platform disclosures |
| `local-tests/` | Local workflow-logic simulation and wave-1 rehearsal kit (synthetic corpora, harness, checker evidence, prompt pack, runbook, demo script) — supporting evidence, not part of the Skill package |

The submittable Skill package is `SKILL.md` + `references/` only, in a
directory named `phoenix-recovery-intelligence` (required by the checker).

## Requirements

- UGREEN AI NAS (UGOS) with Uliya Skills support
- UGREEN Skill Developer Package v0.7.3 and its capability catalog
- Registered experts: `file-agent`, `document-agent`, `knowledge-agent`
- Capabilities: `ug-filesystem` (`find`, `ls`, `stat`, `sha256sum`),
  `ug-document` (`qa`, `extract`, `reconcile`), `ug-knowledge`
  (`collect-evidence`, optional `save-text`)

No external APIs, models, datasets, executables, or custom runtime code are
required. Document text is treated as untrusted evidence, never as
instructions.

## Installation

1. Download or clone this repository:
   `git clone https://github.com/toskaman/UGREEN-PHOENIX.git`
2. Copy the `SKILL.md` file together with the `references/` folder into your
   Skills directory, following the official starter-kit layout
   (see the [hackathon starter kit](https://ai.ugreen.com/pages/hackathon-starter-kit)).
3. Keep the relative structure intact — `SKILL.md` references
   `references/decision-protocol.md`, `references/validation-plan.md`, and
   `references/disclosures.md` by relative path.
4. Run the provided static checker from the Skill Developer Package against
   the Skill folder; proceed only with zero diagnostics.

## Usage

Invoke the Skill in your own language with a project, a failure scenario, and
an explicitly authorized NAS scope, for example:

> "Could we resume the customer portal project if we lost the developer
> workstation? Authorized scope: `/projects/customer-portal` only.
> Report only, no saving."

PHOENIX asks for the scope when it is missing and never assumes blanket
access. Saving the report to the NAS is optional, off by default, and always
requires a separate user request plus platform approval.

## Test status

| Check | Status |
|---|---|
| Static checker (kit 0.7.3, catalog 2.0.0) | ✅ `static-pass`, 0 errors, 0 warnings ([evidence](local-tests/evidence-check-result.json)) |
| Core test A — required config absent from corpus | ✅ Logic validated locally (`NOT FOUND IN SCOPE`, no global claim) · NAS runtime ⏳ ([plan](references/validation-plan.md)) |
| Core test B — present but version-incompatible config | ✅ Logic validated locally (`CONFLICTING`, both sources cited) · NAS runtime ⏳ |
| Edge case — denied access / prompt-injection document | ✅ Logic validated locally (denied, truncated, injection handled) · NAS runtime ⏳ |
| Baseline comparison (filename search vs. generic QA vs. PHOENIX) | ✅ Measured locally (PHOENIX 7/7, filename 3/7, generic QA 1/7) · NAS runtime ⏳ ([report](local-tests/reports/baseline-comparison.md)) |
| Runtime execution on UGREEN AI NAS | ⏳ Untested — no NAS access in Round 1 |

Local simulation: 31/31 checks green (`python local-tests/run-tests.py`)
plus the measured baseline comparison. This validates the workflow logic
only. The 24-hour finalist session plan is in
[local-tests/finalist-runbook.md](local-tests/finalist-runbook.md).
No NAS runtime results are claimed;
static checker success is not a runtime pass. If selected as a finalist, the
planned tests will run during the assigned remote NAS session and this
section will be updated with real evidence, logs, and a demo video. Open
platform questions for UGREEN support are listed in
[local-tests/open-questions-for-ugreen.md](local-tests/open-questions-for-ugreen.md).

## Limitations

- Document-level assessment only: PHOENIX reports documentary readiness, never
  a tested recovery, a running service, or a bootable system.
- Inference can miss dependencies or hallucinate relationships; results are
  constrained by source coverage, model context, NAS permissions, and document
  quality.
- No numeric recovery percentage is produced; file counts are never equated
  with functional recovery.
- Out of scope: NAS snapshot inspection, backup verification, OS restoration,
  recovery automation, isolated-VM recovery testing, and 24/7 monitoring.
- `NOT FOUND IN SCOPE` means a bounded authorized search returned nothing —
  it is never generalized to global absence or impossibility of recovery.
- Secrets are never exposed in reports; credential dependencies are described
  by type only.

## Disclosures

PHOENIX was newly authored for this hackathon (November 2026); no earlier
Skill or external code is bundled. OpenAI ChatGPT (GPT-6) assisted with
reviewing the Developer Package, designing the orchestration, drafting text,
and static validation. Full details in
[references/disclosures.md](references/disclosures.md).

## Links

- Hackathon: [UGREEN Hackathon 2026](https://ai.ugreen.com/pages/ugreen-hackathon)
  · [Devpost](https://ugreenhackathon.devpost.com/)
- Starter kit: <https://ai.ugreen.com/pages/hackathon-starter-kit>
- Round 1 deadline: November 15, 2026, 11:45 PM PT (proposal + initial Skill
  Package, no demo video required)

## License

PolyForm Strict 1.0.0 — see [LICENSE](LICENSE). Same license as the
[OpenBridge](https://github.com/toskaman/openbridge) project: use for any
noncommercial purpose is permitted; distribution, modification, and commercial
use require a separate license from the author.
