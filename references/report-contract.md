# Report contract: Proof Graph and Readiness Passport

How the knowledge-agent serializes findings as text. Mirror these shapes
exactly; they are the native equivalent of the locally validated
renderer. Never invent a node or edge: every line must trace to a real
upstream expert result.

## Proof Graph

Header: `PROOF GRAPH (N nodes, M edges)`.

For each requirement, one block:

```text
[REQ: subject]
  --stated-by--> [DOC: path:line]
  --satisfied-by--> [FILE: path]
```

Node vocabulary: `[REQ: ...]`, `[DOC: path:line]`, `[FILE: path]` (or
`[FACT: observed detail]` when no single file applies),
`[GAP: subject — STATUS: detail]`, `[CLASH: detail]`.

Edge vocabulary (exactly one outcome edge per REQ):

- `stated-by`: the document line that states the requirement (mandatory).
- `satisfied-by`: FOUND evidence (file or observed fact).
- `contested`: CONFLICTING evidence on both sides.
- `blocked-by`: NOT FOUND IN SCOPE, INACCESSIBLE, or UNKNOWN gap.

Footer: `UNRESOLVED: X gaps, Y clashes.`

Consistency rules: every REQ has exactly one `stated-by` edge and
exactly one outcome edge; GAP and CLASH nodes are never dropped to make
a graph look clean; an edge without an upstream source is forbidden.

## Proof Graph with Delta (recheck only)

Header: `PROOF GRAPH WITH DELTA (prior verdict -> current verdict)`.

Same blocks, each REQ suffixed with its transition state:
`[REQ: subject] [RESOLVED]`, `[STILL UNCERTAIN]`, `[UNCHANGED]`,
`[NEW GAP]`. Subjects named in the prior report but absent from current
findings are listed as prior-only and stay uncertain — never silently
resolved.

Footer: `Documentary blockers resolved: N. This is not a tested restoration.`

## Readiness Passport (compact, 7 sections)

1. Identity: project, scope, scenario, assessment time, PHOENIX version.
2. Verdict: the exact verdict line.
3. Requirements: the Proof Graph (or Delta graph on recheck).
4. Evidence limits: counts reviewed / skipped / inaccessible /
   truncated / errors, and completion state.
5. Blockers (prioritized P1/P2), or the Delta graph on recheck.
6. Resolution history (or "None — first assessment" with recheck
   instructions).
7. Next checks: what would expire this passport (new files, version or
   permission changes need a fresh assessment).

Close with the anti-guarantee, verbatim in meaning: this passport
documents evidence reviewed, not a tested recovery; only a real
restoration test proves recoverability.
