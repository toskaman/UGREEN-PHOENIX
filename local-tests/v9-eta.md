# v9 Eta — submission dominance record

## Opening pitches (answer 1 candidates, single-rater scored, not blind)

| # | pitch (28–30w) | comprehension | relevance | differentiation | NAS fit | credibility | memorability |
|---|---|---|---|---|---|---|---|
| P1 | PHOENIX tells you whether your backed-up project can actually be rebuilt: it finds the missing or conflicting dependencies your file search missed, cites the proof, and verifies the fix. | 8 | 9 | 7 | 5 (no NAS) | 7 ("actually" overclaims) | 7 |
| P2 (SHIPPED) | A recovered folder does not prove a recoverable project. PHOENIX checks your authorized NAS files against the project's own documents, reports cited blockers, and re-verifies after you fix them. | 9 | 9 | 8 | 9 | 9 | 9 |
| P3 | PHOENIX is a recovery-readiness investigator for NAS projects: it extracts documented prerequisites, verifies each against stored evidence, and guides a cited recheck until blockers clear. | 7 (jargon) | 7 | 7 | 8 | 8 | 6 |

P2 wins: problem-first, NAS-named, honest re-verify, most memorable.
Limitation: one rater (the builder), no blind panel — recorded, not
hidden.

## Word-count surgery: 492 → 456 (target ≤460 met)

Cuts: A1 pitch rewrite (−11), A3 rules compression (−8), A6/A10
sentence trims (−8), A8 redundancy (−6: "native", "AI/third-party",
"a measured baseline", "run"), A9 test-name accuracy (−3), A2/A4/A7
micro-trims (−5). No substantive claim removed; "Core E" (a test name
with no referent in the validation plan) fixed to "Controls/Closure".

## QA record

- `verify_release.py`: rebuild + ZIP contents/kit-pin/checker +
  PDF structure (10 questions, key phrases) + secret grep + hashes —
  exit 0.
- PDF bytes are NOT reproducible across rebuilds (fpdf2 timestamps;
  observed two hashes for identical content) — PROVENANCE records
  the shipped hash; reproducibility applies to the tree→ZIP path.
- `SUBMISSION_CHECKLIST.md`: machine steps + human-only Devpost steps
  + preservation + deadline.
