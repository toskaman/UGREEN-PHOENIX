# Evidence index (content hashes + provenance)

Working tree verified 2026-11-08 on `main` (v9; content hashes below
are commit-independent — verify with `sha256sum`). CI run for the v9
commit is confirmed post-push in `A SOUMETTRE/PROVENANCE.txt`.
All hashes SHA-256 of the verified bytes (lowercase hex). Checker
file hashes agree with the tree hashes below. Previous release values
live in git history of this file (v8: ZIP 12488 B, PDF 4608 B,
492 words, built from `223b78c`; v7: ZIP 10592 B, PDF 4541 B,
483 words, built from `583b7cd`; v6: ZIP 9960 B, PDF 4482 B,
476 words, built from `e127a0f`; v5: ZIP 9135 B, PDF 4468 B,
475 words, built from `6985a6a`).

## Submission package bytes (in the ZIP)

| File | SHA-256 |
|---|---|
| SKILL.md | `7e75e0cfb76e852ada8a2a0a84a5a667bf6c916ad138188e093632ccaabf7f1c` |
| references/decision-protocol.md | `3daeebc97fa0a5bbf49eaeb40de64ed3c63a823a955378a59b7530702cc89e04` |
| references/validation-plan.md | `e0d825d4991866508a69fa54a44585814b8cd2326bbafd8c0f988d34f6b423ca` |
| references/disclosures.md | `31e97f60205cef92e7773ee6aef847ae76f8d0704f8a61f419f9b33839308804` |
| references/report-contract.md | `ffa6c978e8a7240335293b1b5ec8860299a76f93790fdb335963508e6728c270` |

Checker: `static-pass`, 0 errors, 0 warnings, catalog 2.0.0
(`local-tests/evidence-check-result.json`,
`a15d5f6483f2c6a48e7fbc232fe43e44477f18c9ecdee55656f3ed66caefc333`,
regenerated UTF-8 from the current tree 2026-11-08).

## Release artifacts (`A SOUMETTRE/`, gitignored, v9)

| Artifact | SHA-256 | Size | Notes |
|---|---|---|---|
| phoenix-recovery-intelligence.zip | `58b6ff5426804338d512536a946043ca87bfd9c790eb1641c1b782acdff1ddb1` | 13411 B (< 10 MB) | 5 files, per-file verified, official checker static-pass on exact bytes |
| PHOENIX_UGREEN_Round1_Proposal.pdf | `f0410513331c6a7b9feef6207f52169ff259144222a1cf7c223af91871b14096` | 4452 B (< 1 MB) | 2 pages, 471 answer words (≤ 500; v9.1 planner sentence), hash varies by build timestamp only |
| SHA256SUMS.txt | (manifest of the above) | — | Previous releases preserved in `previous/` + notes |

Rebuild: `python "A SOUMETTRE/build_zip.py"` then
`python "A SOUMETTRE/build_pdf.py"` from the repo root (both self-verifying).

## Verification tooling bytes

| File | SHA-256 |
|---|---|
| local-tests/harness.py | `8b579af75a3e68b576acc51a66a13fd1682651dbe2daf75326a5efb0841402ed` |
| local-tests/run-tests.py | `6bb6ee3cd12789eb4d662a6d38ecd6fb0a265fe338ae07e12711022a22438ded` |
| local-tests/baselines.py | `3fb911a9b0254864f8f88f89ff6ce66b176c1ff7d7656766f50f0f4d6b87c816` |
| local-tests/mutate.py | `4ffbdacd61e847f8d1f6d392ad4742236732d1637d9d2b021666495e482cd03d` |
| local-tests/labels.json | `f52152d8dbdd99193414ee4f4c90e211473fb0458593f13b50109200486a8e46` |
| local-tests/reports/baseline-comparison.md | `3fbe0cf4dfe6d28dbc0e91f3c73efbe1de07cd329584b738104a0664a887450c` |
| local-tests/proofgraph.py | `32f8b03372b28d45251f285b1f1f724348cd5c521406bb6bf0365250b1cd33a1` |
| local-tests/test_proofgraph.py | `648e6a02d160b7f1ef4af470b14e47a412b376dc65309b2b9bfb93796f90cd50` |
| local-tests/native-transfer-report.md | `58ba1da03f357119ae53571aa611a8350aea77a234a5ecc963671913b8ac20e8` |

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
| README.md | `4f91e0568984243764a931b083e1230218cd6a687139c72cae6aed5f662c9b1e` |
| LICENSE | `9eb48619fbc193ab7bb327b090cfcc703000265b83e670f81f231d0b1c43c56e` |
| local-tests/README.md | `a610f4f2a1241f2aad6b2f9fc19966e523a5b2ddd557d90caff377ccab49bd12` |
| local-tests/perf-matrix.md | `24aace7dbfedea2ef694966561c7c13e25d3053c94c645355a7074bef88baac2` |
| local-tests/audit-matrix.md | `963fd902fcbdbc8f44e721dfa457d3be9f39cdecba53e5f53fb0a5b16c19118d` |
| local-tests/commercial-thesis.md | `7c2e508f3b141dc8dbdde6e1ede6a6fff0157e3577273338b0f44a7396f3597e` |
| local-tests/jury-report.md | `8e7f5c480147da8ec071a12cc42394314947f7ac15944452c55eea70dcfe338b` |
| local-tests/assistant-vs-phoenix.md | `e79eee0ca9a47c10db1b28ceb0cc8ba84ad496701348851e1a2dee440009e6e1` |
| local-tests/user-study-protocol.md | `209f59a3a73dba75a6857c43c4b7dacab2be9f239070133ea3e264c9da81d387` |

## v5 reliability program bytes

| File | SHA-256 |
|---|---|
| local-tests/ai-lab/evaluators/aggregate.py | `38c115b539eaa6baa92fa3bd45f01fa0470aea9cf18431a644cac39b29119f09` |
| local-tests/ai-lab/evaluators/normalize.py | `439afa14329be6e0fe9958fccc715dd36d5d4c14fe3a64d68c0fbdc015d5c1a4` |
| local-tests/ai-lab/evaluators/verify.py | `c29eaca2f6df96355e655ee6e189f1ffdee229d668196dae7a4c796642f2e116` |
| local-tests/ai-lab/evaluators/delta.py | `190a9c7880eae72e7745e1649319a9edb79fd082238dc646d7a7fdf2653d77ce` |
| local-tests/ai-lab/prompts/b1c.md | `391fccc3183fca9a4d816934ea4dbcad39fb0b16430f6de5d0f03afe1b99f6eb` |
| local-tests/ai-lab/datasets/ext/labels.json | `743a5d5c2d432d74fef316586358a297c14e0a3c4669a6a02679204401dc55f1` |

Pipeline results (14B local): Track B 6/6, dev 10/10, validation 10/10,
closure-dev 2/2, locked 9/10 (x26 French-constraint gap, recorded not
patched). v6 adds: multilingual m01-m12 12/12 and one locked rescore
10/10 (x26 closed; the original 9/10 stands as the pre-fix record).
v8 adds: 9B Track B 6/6 (TB6 scorer fix, sweep-proven, gold untouched),
Q9 conditional transfer 12/12 on 14B and 9B (fresh cases, transcripts).
Transcripts under `local-tests/ai-lab/reports/transcripts/`.

## CI

Run 42479416422 (commit `da7908a`): 7/7 success — checker (with kit
SHA-256 verification) + tests on ubuntu/windows/macos × Python
3.13/3.14. Prior greens: 42439390834, 42439222409, 42434288731,
42434030405, 42412827209, 42405031294, 42404824165. The run id is
recorded in `A SOUMETTRE/PROVENANCE.txt` and the closing report.
