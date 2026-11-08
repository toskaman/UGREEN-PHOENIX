# Baseline comparison (local measurement)

Methods: `phoenix` (full decision procedure: exact-path checks,
version reconciliation, access handling, source:line citations);
`phoenix_no_reconcile` (contradictions degrade to UNKNOWN);
`phoenix_no_verify` (basename matching instead of exact paths);
`retrieval_plus` (exact paths plus version compare, cited,
abstains only on unfounded versions, no access handling);
`filename_search` (basename match anywhere, versions assumed
satisfied, no citations); `generic_qa` (subject string mentioned
anywhere counts as satisfied, no citations). Non-PHOENIX methods
ignore the access-denied manifest. Each method ran 3x per case;
verdicts below are the stable result.

| method | verdict accuracy | blocker recall | false allegations | abstention | citation precision | repeatability | mean ms/case |
|---|---|---|---|---|---|---|
| phoenix | 8/8 | 5/5 | 0 | 2/2 | 22/22 rows cited | 8/8 stable | 4.0 |
| phoenix_no_reconcile | 6/8 | 3/5 | 0 | 2/2 | 22/22 rows cited | 8/8 stable | 4.0 |
| phoenix_no_verify | 6/8 | 4/5 | 0 | 1/2 | 22/22 rows cited | 8/8 stable | 3.6 |
| retrieval_plus | 6/8 | 5/5 | 0 | 0/2 | 22/22 rows cited | 8/8 stable | 2.0 |
| filename_search | 3/8 | 2/5 | 0 | 0/2 | 0/22 rows cited | 8/8 stable | 2.4 |
| generic_qa | 1/8 | 0/5 | 0 | 0/2 | 0/22 rows cited | 8/8 stable | 1.5 |

## Extended metrics (absolute counts)

| method | blocker precision tp/(tp+fp) | false clears | false blockers | version-conflict detection |
|---|---|---|---|---|
| phoenix | 5/(5+0) | 0 | 0 | 3/3 |
| phoenix_no_reconcile | 3/(3+0) | 0 | 0 | 1/3 |
| phoenix_no_verify | 4/(4+1) | 1 | 1 | 3/3 |
| retrieval_plus | 5/(5+1) | 0 | 1 | 3/3 |
| filename_search | 2/(2+1) | 3 | 1 | 1/3 |
| generic_qa | 0/(0+0) | 5 | 0 | 0/3 |

## Per-case verdicts

| case | ground truth | phoenix | no_reconcile | no_verify |
|---|---|---|---|---|
| core-a | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-b | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | INSUFFICIENT EVIDENCE | DOCUMENTARY BLOCKER IDENTIFIED |
| core-c | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-d | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED |
| edge | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE |
| edge-2 | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | INSUFFICIENT EVIDENCE | DOCUMENTARY BLOCKER IDENTIFIED |
| edge-3 | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | DOCUMENTARY BLOCKER IDENTIFIED |
| scale | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED |

## Per-case verdicts, naive methods

| case | ground truth | retrieval_plus | filename_search | generic_qa |
|---|---|---|---|---|
| core-a | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-b | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-c | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-d | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge | INSUFFICIENT EVIDENCE | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge-2 | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge-3 | INSUFFICIENT EVIDENCE | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| scale | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |

Local simulation only — not NAS runtime evidence. Ground truth:
`labels.json` (predeclared before measurement).