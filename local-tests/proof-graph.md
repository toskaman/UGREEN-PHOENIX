# Recovery Proof Graph (design, v5)

A human-readable dependency graph emitted as plain text inside the
PHOENIX report. No graph database, no executable, no new capability:
the knowledge-agent serializes edges it already collects for the
evidence table.

## Node types

- REQ: a documented prerequisite (subject + constraint).
- FILE: an observed file (path + bytes + optional hash).
- DOC: a source document (path + line range).
- GAP: a missing/inaccessible/unverifiable requirement.
- CLASH: a contradiction between two sources.
- FACT: an observed version fact satisfying a named-capability requirement
  (carries the provision's path:line citation).

## Edge types

- `REQ --stated-by--> DOC:path:line`
- `REQ --satisfied-by--> FILE:path` (with version note)
- `REQ --satisfied-by--> FACT: <provision citation>` (named capabilities)
- `REQ --blocked-by--> GAP` (with reason)
- `REQ --contested--> CLASH` (DOC A vs DOC B)
- `REQ --alternative--> REQ` (OR-group)

## Text format

```text
PROOF GRAPH (7 nodes, 8 edges)
[REQ: render preset >=2024]
  --stated-by--> [DOC: docs/restore-guide.md:6]
  --blocked-by--> [GAP: render/preset.yaml not in scope]
  --contested--> [CLASH: guide requires render/preset.yaml
                  vs stale old/preset.yaml:1 "superseded"]
[REQ: scene file]
  --stated-by--> [DOC: docs/restore-guide.md:4]
  --satisfied-by--> [FILE: scenes/shot01.blend, 28 B]
UNRESOLVED: 1 gap, 1 clash. Next: locate render/preset.yaml.
```

## Rules

- Every edge cites a path:line the user can open.
- GAP and CLASH nodes are never dropped, even when the verdict is clear.
- The graph is derived from the same findings as the evidence table;
  any divergence between the two is a report bug.
- Recovery Delta re-emits the graph with per-node states
  (RESOLVED/STILL BLOCKED/NEW/...), so the user sees what changed.

## Validation

- Unit: graph/evidence-table consistency (same finding set).
- Model: extraction must list every graph node (Arch B rows map 1:1).
- User: locate-the-blocker task time vs prose-only report (protocol in
  `local-tests/user-study-protocol.md`).
