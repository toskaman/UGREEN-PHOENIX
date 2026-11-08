# v9.1 compliance forensics

Rule-source caveat: `devpost.com/rules` returned HTTP 403 to direct
fetch in every session including this one. Hackathon-rule conclusions
below rest on prior-session mirrors + the pinned local kit; kit-cited
conclusions were re-verified in-tree this session. Where only a
mirror exists, this doc says MIRROR and names the organizer question.

## 1. Participant eligibility — PASS (2 questions queued)

Checklist (individual entry, solo, no team):

- Individual (not corporation) entry: PASS — entrant is a natural
  person; no company is named as entrant anywhere in the submission.
- Residence/age: PASS (operator-confirmed prior cycles; no rule text
  re-verified — MIRROR).
- Ownership: PASS — `references/disclosures.md`: PHOENIX authored as
  a new Skill for this hackathon; no prior project bundled.
- Team/permissions: PASS — solo; no collaborator permissions needed.
- Originality/period: PASS — new work, committed history proves
  development during the contest window.
- Third-party IP: PASS — no third-party code bundled (disclosure in
  PDF + disclosures.md); UGREEN kit is a platform dependency under
  UGREEN terms, not redistributed.
- Existing business (OpenBridge): PASS-BY-ANALYSIS — owning an
  unrelated registered company does not make the company the entrant
  and does not transfer PHOENIX ownership; but the rules' org/team
  wording is genuinely ambiguous (MIRROR).

Organizer questions (ask only if selected; do not assert law):
1. Confirm an individual entrant who owns an unrelated registered
   company remains eligible, with the entry owned by the individual.
2. Confirm no additional ownership declaration is needed for solo
   entries beyond the Devpost form.

## 2. License compatibility — CONDITIONAL (narrow, no auto-change)

PolyForm Strict 1.0.0, exact provisions:

- Copyright license (LICENSE:11): do anything EXCEPT distributing
  or making changes/new works. Judges installing, running, and
  evaluating the Skill = use, not distribution → judging rights OK.
- Noncommercial (LICENSE:17-27): hackathon evaluation is a
  permitted noncommercial purpose → Round 1/2 testing OK.
- No-distribution vs sponsor promotion: if the official rules
  require entrants to grant the sponsor redistribution/showcase
  rights beyond evaluation display, §Copyright License ("other than
  distributing") does not grant them → CONDITIONAL.
- No sublicensing (§No Other Rights): organizers cannot pass a
  sublicense to third parties; direct evaluation unaffected.

Narrowest correction if organizers object (owner approval needed):
add a `HACKATHON-EVALUATION-ADDENDUM.md` granting UGREEN + Devpost
judges a non-exclusive, non-transferable right to install, execute,
display, and archive the submitted ZIP/PDF for judging and winner
showcase through the contest + 12 months — without changing the
repo's noncommercial license. NOT applied without owner approval.

## 3. Rule compliance — PASS (kit-verified + measured)

| requirement | source | v9 status |
|---|---|---|
| 10 proposal questions | MIRROR (rules) | 10/10 present in PDF bytes |
| ≤500 answer words | MIRROR (rules) | 471 after planner sentence (rebuilt + asserted) |
| PDF ≤1 MB | MIRROR (rules) | 4362 B, 2 pages |
| ZIP ≤10 MB | MIRROR + kit 10MiB | 13411 B; builder asserts both |
| SKILL.md + linked refs only | kit skill-format + checker root rule | 5 files, static-pass 0/0 |
| per-file ≤1MB, ≤100 files | kit check-lib.mjs:14-16 | asserted pre-zip + checker |
| frontmatter/capabilities | kit catalog 2.0.0 | file/document/knowledge agents only |
| disclosures (AI, third-party) | MIRROR (rules) | PDF disclosure + disclosures.md |
| no credentials/private data | MIRROR + verify_release grep | grep clean |
| no unobserved runtime claims | MIRROR (honesty) | "NAS runtime not tested" in PDF header |

Verdict: no BLOCKED item. One CONDITIONAL (license showcase scope)
with a drafted, unapplied narrow fix. Two organizer questions queued.
