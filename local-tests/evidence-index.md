# Evidence index (content hashes + provenance)

Working tree verified 2026-11-07 on `main` (release built from
`c44c4dd`; `SKILL.md`+`references/` byte-identical in the final commit —
verified by empty diff, see closing report). All hashes SHA-256 of the
verified bytes. Checker file hashes agree with the tree hashes below.

## Submission package bytes (in the ZIP)

| File | SHA-256 |
|---|---|
| SKILL.md | `01E3CA23AF92F7F449A25A1BD68A3EFADE58FDE52D28301245AF96E92417AC32` |
| references/decision-protocol.md | `E4CF314C45788B054EAD6802E481FE5C0BB484A2E22B4249FEE74EA191148618` |
| references/validation-plan.md | `7174F27FBAA95DD8F132B488E90F95CC0D71ADDB9884F3AFD8D8524C4C9FC0E5` |
| references/disclosures.md | `31E97F60205CEF92E7773EE6AEF847AE76F8D0704F8A61F419F9B33839308804` |

Checker: `static-pass`, 0 errors, 0 warnings, catalog 2.0.0
(`local-tests/evidence-check-result.json`,
`682FE0ACCA736B97465697C9CA0064E879C0A914C1D5A7E3660CBD76CDDC3C32`).

## Release artifacts (`A SOUMETTRE/`, gitignored, built from `c44c4dd`)

| Artifact | SHA-256 | Size | Notes |
|---|---|---|---|
| phoenix-recovery-intelligence.zip | `d4b788784ca2b81f5add560d6154f607050280b1fb982105a56288cbb4ae6205` | 7372 B (< 10 MB) | 4 files, per-file verified, byte-identical across rebuilds |
| PHOENIX_UGREEN_Round1_Proposal.pdf | `48ebf48b57a4815258773a62b3d6e7d13a6fda2eccfac3011abe90d90f984f21` | 3778 B (< 1 MB) | 1 page, 418 answer words (≤ 500), hash varies by build timestamp only |
| SHA256SUMS.txt | (manifest of the above) | — | Previous release preserved in `previous/` + PROVENANCE.txt |

Rebuild: `python "A SOUMETTRE/build_zip.py"` then
`python "A SOUMETTRE/build_pdf.py"` from the repo root (both self-verifying).

## Verification tooling bytes

| File | SHA-256 |
|---|---|
| local-tests/harness.py | `EB625EC3676A71DEB5BFBED6C928A59BD76B391816EE60D39AF727BFADFE7305` |
| local-tests/run-tests.py | `9D5428B611382FBE48203AB0996B54B56185A354757DA0C8CF64762FF15E2C0F` |
| local-tests/baselines.py | `3FB911A9B0254864F8F88F89FF6CE66B176C1FF7D7656766F50F0F4D6B87C816` |
| local-tests/mutate.py | `0C4C64E5A3400A1119A67DD252CC0CF5BAAC02A8180C41B5001D7221690D4096` |
| local-tests/labels.json | `F52152D8DBDD99193414EE4F4C90E211473FB0458593F13B50109200486A8E46` |
| local-tests/reports/baseline-comparison.md | `B0A211805076FDFBB4ED467A4D0F3965F20CDBC5C20B379D8167BAC886667B36` |

## Docs

| File | SHA-256 |
|---|---|
| README.md | `E714F78989D3EBA407AA9B11A147A573A5D13E7B06A7632E2B28B67C8592D745` |
| LICENSE | `9EB48619FBC193AB7BB327B090CFCC703000265B83E670F81F231D0B1C43C56E` |
| local-tests/README.md | `1D8F85D988C8AB24D2C1C20A3752D68FCB7D067266694B0034E1D3A8267AFF54` |
| local-tests/perf-matrix.md | `24AACE7DBFEDEA2EF694966561C7C13E25D3053C94C645355A7074BEF88BAAC2` |
| local-tests/audit-matrix.md | `65CC2756C1B01A3C7FFDD02B08CD3C5A361D7168D71B9FEDDD0825047B8AA457` |
| local-tests/commercial-thesis.md | `73E3E44FEFBBA73059AE8A080BC254E584A970B19D4D7BC9C55A1709DE2422AD` |
| local-tests/jury-report.md | `140760B12EB144ECA50171EA494168A2C1FAFAA6039CB4BE66BC37506938FB79` |

## CI

Run 42400074403 (commit `410ca6c`): 5/5 success — checker + tests on
ubuntu/windows × Python 3.13/3.14. Run 42400566200 (commit `e8fbd25`):
success. Run 42401851303 (commit `2ae662a`): success. The closing report
names the latest run.
