# Evaluation tracks (A = deterministic, B = model inference)

## Track A — Deterministic logic (VERIFIED)

What: exact path handling, version comparison, scope safety, verdict
ordering, report contracts, reproducibility, mutation kills.
How: `run-tests.py` (71 checks), `mutate.py` (16/16), `run-baseline.py`
(6 deterministic methods × 8 labeled cases × 3 runs).
Proves: the workflow LOGIC is correct. Proves nothing about any model.

## Track B — AI reasoning (local models only, disclosed)

What: whether real language-model execution extracts requirements from
natural-language documents, reconciles conflicts, cites sources, abstains
honestly, and emits the protocol verdict.
How: `track-b/run-trackb.py` feeds held-out natural-language cases
(`track-b/corpus/tb1..tb6`, no markers) to local Ollama models with the
frozen prompt `track-b/prompt.md` (temperature 0), saves raw transcripts
(`track-b/transcripts/*.json`), and grades them against human-authored
`track-b/labels.json` in `track-b/results.md`.
Proves: feasibility of the reasoning task on commodity local models.
Does NOT prove: Uliya behavior, NAS behavior, transfer to other models,
or production quality. Sample is tiny (6 cases); no statistics beyond
counts. Never cite Track B as "AI reasoning accuracy" without the
denominator and the model name.

## Honesty rules

- Track A green never becomes a Track B claim.
- Track B results always ship with model id, prompt hash, runtime,
  transcripts, and the grading rubric.
- Held-out cases (`tb*`) share no text with fixtures or prompts.
- `generic_qa` (substring proxy) is the text-only chatbot stand-in for
  the assistant-vs-PHOENIX comparison — labeled as such, never as an LLM.
