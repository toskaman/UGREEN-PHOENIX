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
| phoenix | 7/7 | 5/5 | 0 | 1/1 | 18/18 rows cited | 7/7 stable | 2.1 |
| filename_search | 3/7 | 2/5 | 0 | 0/1 | 0/18 rows cited | 7/7 stable | 2.1 |
| generic_qa | 1/7 | 0/5 | 0 | 0/1 | 0/18 rows cited | 7/7 stable | 1.3 |

## Per-case verdicts

| case | ground truth | phoenix | filename_search | generic_qa |
|---|---|---|---|---|
| core-a | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-b | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-c | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| core-d | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge | INSUFFICIENT EVIDENCE | INSUFFICIENT EVIDENCE | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| edge-2 | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |
| scale | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | DOCUMENTARY BLOCKER IDENTIFIED | NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES |

Local simulation only — not NAS runtime evidence. Ground truth:
`labels.json` (predeclared before measurement).