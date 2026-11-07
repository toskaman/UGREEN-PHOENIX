# Baseline comparison (local measurement)

Methods: `phoenix` (harness.py decision procedure with exact-path
checks, version reconciliation, access handling, and source:line
citations) vs `filename_search` (basename match anywhere, versions
assumed satisfied, no citations) vs `generic_qa` (subject string
mentioned anywhere counts as satisfied, no citations). Baselines
ignore the access-denied manifest. Each method ran 3x per case;
verdicts below are the stable result.

| method | verdict accuracy | blocker recall | false allegations | abstention | citation precision | repeatability | mean ms/case |
|---|---|---|---|---|---|---|
| phoenix | 8/8 | 5/5 | 0 | 2/2 | 22/22 rows cited | 8/8 stable | 2.5 |
| filename_search | 3/8 | 2/5 | 0 | 0/2 | 0/22 rows cited | 8/8 stable | 1.8 |
| generic_qa | 1/8 | 0/5 | 0 | 0/2 | 0/22 rows cited | 8/8 stable | 1.2 |

## Per-case verdicts

| case | ground truth | phoenix | filename_search | generic_qa |
|---|---|---|---|---|
| core-a | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-b | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-c | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-d | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge-2 | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge-3 | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| scale | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |

Local simulation only — not NAS runtime evidence. Ground truth:
`labels.json` (predeclared before measurement).