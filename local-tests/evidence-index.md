# Evidence index (content hashes + provenance)

Working tree verified 2026-11-07 on `main` (v4 release built from
`ef776f0`; CI 42404824165 green). All hashes SHA-256 of the verified
bytes (lowercase hex). Checker file hashes agree with the tree hashes
below. Previous release values live in git history of this file.

## Submission package bytes (in the ZIP)

| File | SHA-256 |
|---|---|
| SKILL.md | `b039c7853d4cad5697cc7f161b555563ed167d6fad8df16216f4b435443947b0` |
| references/decision-protocol.md | `d5e582f0211cc642119ffb9f3c0bd7a0de662cb5d40d04c7c5624f57cc2dff58` |
| references/validation-plan.md | `7174f27fbaa95dd8f132b488e90f95cc0d71addb9884f3afd8d8524c4c9fc0e5` |
| references/disclosures.md | `31e97f60205cef92e7773ee6aef847ae76f8d0704f8a61f419f9b33839308804` |

Checker: `static-pass`, 0 errors, 0 warnings, catalog 2.0.0
(`local-tests/evidence-check-result.json`,
`cb8ca82da5fa7f74538bac6ddcd3b0de883af8dece96d9435f2d6a20526feaa4`,
regenerated UTF-8 from the current tree 2026-11-07).

## Release artifacts (`A SOUMETTRE/`, gitignored, built from `ef776f0`)

| Artifact | SHA-256 | Size | Notes |
|---|---|---|---|
| phoenix-recovery-intelligence.zip | `53ffa42f87dd50e83c2188ab8a4cefe0e25967ac833384f48474acefc99508af` | 8196 B (< 10 MB) | 4 files, per-file verified, official checker static-pass on exact bytes |
| PHOENIX_UGREEN_Round1_Proposal.pdf | `3dda751a2bec739704baffd0e6b32db341f8622e551b49bd88d5d19d6c251dc2` | 4555 B (< 1 MB) | 2 pages, 499 answer words (≤ 500), hash varies by build timestamp only |
| SHA256SUMS.txt | (manifest of the above) | — | Previous releases preserved in `previous/` + notes |

Rebuild: `python "A SOUMETTRE/build_zip.py"` then
`python "A SOUMETTRE/build_pdf.py"` from the repo root (both self-verifying).

## Verification tooling bytes

| File | SHA-256 |
|---|---|
| local-tests/harness.py | `8a93892e1ca1774e0df0d20736227eb22818ffc02861e9ac8553a5381e1a2672` |
| local-tests/run-tests.py | `c1af695d636cbad4f5bcde5ed12a9a242f6aa7163c9d7065ddf3f80a84a6e194` |
| local-tests/baselines.py | `3fb911a9b0254864f8f88f89ff6ce66b176c1ff7d7656766f50f0f4d6b87c816` |
| local-tests/mutate.py | `c4bbde37052f56da3845c54a65b31a55325cd81c07776397fa89c1754baad612` |
| local-tests/labels.json | `f52152d8dbdd99193414ee4f4c90e211473fb0458593f13b50109200486a8e46` |
| local-tests/reports/baseline-comparison.md | `8f96b370a89e89653e4eccd66a8b476e804aaaf6d8efaa36532bc0a977be8974` |

## Track B bytes (held-out inference evaluation)

| File | SHA-256 |
|---|---|
| local-tests/tracks.md | `391bb5516613d52f0514600a0476e873e81211e3297c9b6ec2302304527b3371` |
| local-tests/track-b/prompt.md | `e6846d9cceec0141345c4557f4267edfecc10f97cdb9a500c3cf919e17288eef` |
| local-tests/track-b/labels.json | `2d6b16e42967552ac5dd1aaa43e792309d7e6bd0bb4a98aa9c82504b19f552e4` |
| local-tests/track-b/run-trackb.py | `332ca1b76377c883a52ec00a229e2a0bb5441293068713b86e6e29745f8fc3bd` |
| local-tests/track-b/results.md | `d612a3b89f5a5d714e27230dd9f3cf8331facd71d648585a2c619736e2a3911e` |

Prompt sha prefix `e6846d9cceec0141` matches the `prompt_sha` recorded
in every transcript under `local-tests/track-b/transcripts/`.
Transcripts are committed evidence; re-grade from them any time.

## Docs

| File | SHA-256 |
|---|---|
| README.md | `cb27eded8863f535a5b9aad88028cf7e6e91722b44533c6f24cbf9e7d297aac9` |
| LICENSE | `9eb48619fbc193ab7bb327b090cfcc703000265b83e670f81f231d0b1c43c56e` |
| local-tests/README.md | `a610f4f2a1241f2aad6b2f9fc19966e523a5b2ddd557d90caff377ccab49bd12` |
| local-tests/perf-matrix.md | `24aace7dbfedea2ef694966561c7c13e25d3053c94c645355a7074bef88baac2` |
| local-tests/audit-matrix.md | `65cc2756c1b01a3c7ffdd02b08cd3c5a361d7168d71b9feddd0825047b8aa457` |
| local-tests/commercial-thesis.md | `279120086a88ee0d742cb80fc9108f648c03f0ba65381f00a942b78824250bb4` |
| local-tests/jury-report.md | `9b16510c3398b1859eedb7eda1c5707e598eba80edba76f97a149e35eaacee2d` |
| local-tests/assistant-vs-phoenix.md | `e79eee0ca9a47c10db1b28ceb0cc8ba84ad496701348851e1a2dee440009e6e1` |
| local-tests/user-study-protocol.md | `2428dd73a6679ed4763eb508e079eb142376af0143b6a91586adbb0e351afe85` |

## CI

Run 42404824165 (commit `ef776f0`): 7/7 success — checker (with kit
SHA-256 verification) + tests on ubuntu/windows/macos × Python
3.13/3.14. Prior: 42404524365 failed (63-char kit-hash typo in the new
checksum step — fixed same-day in `ef776f0`); 42402972179 and earlier
green. The closing report names the latest run.
