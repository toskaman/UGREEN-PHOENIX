# ai-lab: developer-only multi-model research harness (v5)

NOT part of the Uliya Skill. Nothing under `ai-lab/` ships in the
submission ZIP. No credentials live here — the Vultr key comes only
from process env (`VULTR_INFERENCE_API_KEY`, else `VULTR_API_KEY`).

## Safety rules

- Synthetic corpora only. Never send customer, private, or NAS data.
- Every paid call passes the budget ledger first (worst-case estimate)
  and is recorded after (actual usage). Caps: $10, 200 requests.
- Returned model id must equal the requested id (modulo documented
  `-normalize`); silent substitution rejects the run.
- `finish_reason == length` marks a case TRUNCATED, never a valid score.
- 401 stops the credential path immediately (no retries). 429/5xx retry
  at most twice. Never retry 400.
- Transcripts and the ledger contain no key material (asserted).

## Layout

- `config.py` — model table, pricing (source: /v1/models 2026-11-07), caps
- `budget.py` — append-only JSONL ledger, atomic + locked accounting
- `providers/vultr.py`, `providers/ollama.py` — inference adapters
- `datasets/trackb.py` — v4 held-out corpus loader (same feed contract)
- `evaluators/verdict.py` — verdict parse, citation resolve, forbidden scan
- `experiments/smoke.py` — Stage 1: 1 tiny call per Vultr model
- `experiments/run_bench.py` — model x cases runner with resume
- `tests/test_harness.py` — offline unit tests (run before any spend)
- `reports/` — `ledger.jsonl` + `transcripts/` (committed evidence)

## Campaign order

1. `python local-tests/ai-lab/tests/test_harness.py` (must be green)
2. `python local-tests/ai-lab/experiments/smoke.py` (~$0.001)
3. `python local-tests/ai-lab/experiments/run_bench.py --model ...`
