# PHOENIX local tests (simulation only)

This folder validates the PHOENIX **workflow logic** on a synthetic local
corpus. It is NOT a NAS runtime test and proves nothing about Uliya experts,
NAS permissions, or model quality on a real device.

## Layout

- `corpus/core-a/` — synthetic project whose deployment guide requires an
  absent `config/prod-config.yaml` (expects `NOT FOUND IN SCOPE`).
- `corpus/core-b/` — synthetic project whose `runtime.yaml` declares
  `runtime 2.4.1` against a required `runtime >= 3.0` (expects `CONFLICTING`).
- `corpus/edge/` — access-denied file, truncated document, and an embedded
  instruction that must be ignored (expects `INSUFFICIENT EVIDENCE`).
- `harness.py` — simulates discover → extract → verify → report and emits a
  PHOENIX-style evidence report with verdict.
- `run-tests.py` — runs the harness on the three corpora and asserts the
  exact labels required by `references/validation-plan.md`.
- `reports/` — generated reports (regenerate with `run-tests.py`).
- `evidence-check-result.json` — real output of the official static checker
  (`static-pass`, 0 errors, 0 warnings).

## Run

```sh
python run-tests.py
```

## Honesty rules

- Local green tests never become NAS claims. The main README reports them
  only as "local workflow-logic simulation".
- No corpus file is read outside its case scope; denied files are never
  opened (verified by a no-leak assertion).
- Embedded instructions in corpus documents are untrusted text and are never
  executed (verified by assertions on the report content).
