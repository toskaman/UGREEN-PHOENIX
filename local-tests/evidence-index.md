# Evidence index (content hashes + provenance)

Working tree verified 2026-11-08 on `main` (v6; content hashes below
are commit-independent — verify with `sha256sum`). CI run for the v6
sync commit is confirmed post-push in `A SOUMETTRE/PROVENANCE.txt`.
All hashes SHA-256 of the verified bytes (lowercase hex). Checker
file hashes agree with the tree hashes below. Previous release values
live in git history of this file (v5: ZIP 9135 B, PDF 4468 B,
475 words, built from `6985a6a`).

## Submission package bytes (in the ZIP)

| File | SHA-256 |
|---|---|
| SKILL.md | `4672998f7e0d119592c193d9232c9c70c8d83adb734e56df97585be417b41e9d` |
| references/decision-protocol.md | `1428e58acb0aa0261b34d70285f42bff86f31c1633194768b5f746b1958e925d` |
| references/validation-plan.md | `e0d825d4991866508a69fa54a44585814b8cd2326bbafd8c0f988d34f6b423ca` |
| references/disclosures.md | `31e97f60205cef92e7773ee6aef847ae76f8d0704f8a61f419f9b33839308804` |

Checker: `static-pass`, 0 errors, 0 warnings, catalog 2.0.0
(`local-tests/evidence-check-result.json`,
`1b59a7973386837fbff4d525cc58f3e313605414bc9190fb5af946a80afa50af`,
regenerated UTF-8 from the current tree 2026-11-08).

## Release artifacts (`A SOUMETTRE/`, gitignored, v6)

| Artifact | SHA-256 | Size | Notes |
|---|---|---|---|
| phoenix-recovery-intelligence.zip | `005249f016f6b0ec4587a7937feefaee39483c0fde03e848891620d6d828826f` | 9960 B (< 10 MB) | 4 files, per-file verified, official checker static-pass on exact bytes |
| PHOENIX_UGREEN_Round1_Proposal.pdf | `173e378b562716bae29c065e014d03a6b62b150c5e4dc2569b3e28805cfe66fb` | 4482 B (< 1 MB) | 2 pages, 476 answer words (≤ 500), hash varies by build timestamp only |
| SHA256SUMS.txt | (manifest of the above) | — | Previous releases preserved in `previous/` + notes |

Rebuild: `python "A SOUMETTRE/build_zip.py"` then
`python "A SOUMETTRE/build_pdf.py"` from the repo root (both self-verifying).

## Verification tooling bytes

| File | SHA-256 |
|---|---|
| local-tests/harness.py | `d108391d3ea00d6e7e4103774bcd7cdaf5c3627f0e1a6dc7cd0164316c66f2f0` |
| local-tests/run-tests.py | `06e9969acbb4ceab1f3b19d617cc5c0ba37ead8e62ae951234219617cd33285c` |
| local-tests/baselines.py | `3fb911a9b0254864f8f88f89ff6ce66b176c1ff7d7656766f50f0f4d6b87c816` |
| local-tests/mutate.py | `c4bbde37052f56da3845c54a65b31a55325cd81c07776397fa89c1754baad612` |
| local-tests/labels.json | `f52152d8dbdd99193414ee4f4c90e211473fb0458593f13b50109200486a8e46` |
| local-tests/reports/baseline-comparison.md | `599159e3799495211206eae7ff8dd7f003192b25a815d3a83c93d58005c626d7` |
| local-tests/proofgraph.py | `0089470babe3c1e9e3c6394953e166db2de60c2e6e19278731a44ca17b4c9e58` |
| local-tests/test_proofgraph.py | `d5926eedc3760c100a7f0a82602091194c0dd10459fd899be096a2d82492765f` |
| local-tests/native-transfer-report.md | `a7720e4a73adc41b1cebbec8067d3ec5f06be870da6598541c24dbfb0181d7ec` |

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
| README.md | `91e0261d56aa60802fc464d113eb3eba43114e3bf57e1a84e5cb1f551dcea1ea` |
| LICENSE | `9eb48619fbc193ab7bb327b090cfcc703000265b83e670f81f231d0b1c43c56e` |
| local-tests/README.md | `a610f4f2a1241f2aad6b2f9fc19966e523a5b2ddd557d90caff377ccab49bd12` |
| local-tests/perf-matrix.md | `24aace7dbfedea2ef694966561c7c13e25d3053c94c645355a7074bef88baac2` |
| local-tests/audit-matrix.md | `65cc2756c1b01a3c7ffdd02b08cd3c5a361d7168d71b9feddd0825047b8aa457` |
| local-tests/commercial-thesis.md | `4d56b4c4816ec067c62f7b807526932c1f2f2948af26a4101ef04740c737efac` |
| local-tests/jury-report.md | `eb30109328427fa444ef783573531b25ace15de8b78635d79287fd4dd8d7e6ec` |
| local-tests/assistant-vs-phoenix.md | `e79eee0ca9a47c10db1b28ceb0cc8ba84ad496701348851e1a2dee440009e6e1` |
| local-tests/user-study-protocol.md | `2428dd73a6679ed4763eb508e079eb142376af0143b6a91586adbb0e351afe85` |

## v5 reliability program bytes

| File | SHA-256 |
|---|---|
| local-tests/ai-lab/evaluators/aggregate.py | `e4f339532dac0ebe5a69f3bad517320632a3a321b357675f9885004c439fc175` |
| local-tests/ai-lab/evaluators/normalize.py | `a278c8a26ee9e4f29e38a2a7be32e581ccfba5441dbc7297c91e5408b5747cc6` |
| local-tests/ai-lab/evaluators/verify.py | `26573c32af7e38a70cf418cbad3b3a2c2ccc8a450abd83e2474b92ec6ddf2f35` |
| local-tests/ai-lab/evaluators/delta.py | `14a718cd0ecbb06e5c990c1ffe678dff4af1729fdf6a3756d1d007085f532ff7` |
| local-tests/ai-lab/prompts/b1c.md | `486b7262fc2135811261214cea8cf512aac730a375845789d9b7b3471602c2cd` |
| local-tests/ai-lab/datasets/ext/labels.json | `fc58a8bd8ef6b8d386b53cc33086780f0314884e84cf396e2e295f103d2c238c` |

Pipeline results (14B local): Track B 6/6, dev 10/10, validation 10/10,
closure-dev 2/2, locked 9/10 (x26 French-constraint gap, recorded not
patched). v6 adds: multilingual m01-m12 12/12 and one locked rescore
10/10 (x26 closed; the original 9/10 stands as the pre-fix record).
Transcripts under `local-tests/ai-lab/reports/transcripts/`.

## CI

Run 42412827209 (commit `6985a6a`): 7/7 success — checker (with kit
SHA-256 verification) + tests on ubuntu/windows/macos × Python
3.13/3.14. Prior greens: 42405031294, 42404824165. v6 CI (with ai-lab
offline + proofgraph suites) is confirmed post-push; the run id is
recorded in `A SOUMETTRE/PROVENANCE.txt` and the closing report.
