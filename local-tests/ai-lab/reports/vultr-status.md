# Vultr Serverless Inference status: BLOCKED-CREDENTIALS (2026-11-07)

## What was verified

- `GET /v1/models` returns HTTP 200 with a 33-model catalogue. This
  endpoint is public (no-auth probe below); it never validated any key.
- `POST /v1/chat/completions` with the `VULTR_API_KEY` env credential
  (36-char general infrastructure key) returns **HTTP 401**. That
  credential path is closed per policy (no retries attempted).
- `D:\Hackatons\Vultr\reversa\infrastructure\.env` contains an empty
  `VULTR_INFERENCE_API_KEY=` slot (value length 0). No other inference
  credential exists in env or in the Vultr project tree (searched names
  and non-empty assignments; values never displayed).
- Spend so far: $0.00, 0 paid requests. The ledger is armed and empty.

## What is ready

- `ai-lab` harness: offline tests 20/20, budget ledger ($10 / 200 req),
  model-identity verification, truncation rejection, transcript format.
- Selected Vultr models (from live catalogue + pricing): `glm-5.3`,
  `deepseek-v4.1-flash-1017`, `mimo-v2.6-flash`, `muse-glimmer-30b`.
- Campaign plan staged in `reports/campaign-vultr.md` (to be written).

## Unblock action (human, 2 minutes)

1. Open https://console.vultr.com/inference/ and create a Serverless
   Inference API key (subscription-gated; infra credits may not apply).
2. Set `VULTR_INFERENCE_API_KEY=<key>` in
   `D:\Hackatons\Vultr\reversa\infrastructure\.env` (or process env).
3. Tell the agent to run `experiments/smoke.py`, then the staged campaign.

## No-auth catalogue probe (evidence)

`GET /v1/models` with NO Authorization header still returns 200,
proving the catalogue is public and the earlier 200 never authenticated
the infra key. (See probe output in session log.)
