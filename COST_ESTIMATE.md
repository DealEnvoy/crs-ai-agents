# COST_ESTIMATE (one full real run, not yet run)

Computed 2 Nov 2026 by `estimate_cost.py` from the real prompt text (system + user + pack) counted locally with tiktoken (o200k_base, used as a proxy for all three providers). Output is in `cost_estimate.json`. No model was called.

Shape of one full run: 16 packs x 2 epochs x 3 models = **96 reviewer calls**, plus **48 grader calls** (faulty packs where the reviewer produced a finding; the estimate assumes all 48 happen). Average prompt about 1,455 tokens (1,073 to 1,693 per pack; 23,282 tokens for one pass over the 16 packs).

List prices used: Claude Fable 5.1 and GPT-6 Astra $10 in / $50 out per M tokens. Gemini 4 Argon $2 in / $10 out per M tokens **until 30 Nov 2026** (after that date the guard refuses Argon until prices are updated).

| Scenario | Reviewer output per call | Grader output | Safety margin on input | **Total for the full run** |
|---|---|---|---|---|
| low | 400 tokens | 100 | 1.0 | **$2.85** |
| mid (best guess) | 1,200 | 150 | 1.1 | **$5.89** |
| high (includes hidden reasoning) | 2,500 | 250 | 1.25 | **$10.83** |
| worst (every call hits max_tokens 4000) | 4,000 | 600 | 1.25 | **$16.72** |

Per-model split in the mid case: Fable $2.43 reviewer + $0.24 grading, Astra $2.43 + $0.05, Argon $0.49 + $0.24.

What the estimate does not include: provider retries, hidden "thinking" tokens beyond the stated output, and the reserve rule in `cost_guard.py` (which reserves worst-case cost per call and is much more conservative than these numbers: it may refuse late calls near the cap, which will not happen at these sizes). Even the worst case is about one sixth of the $100 cap, so a first run plus two or three reruns fits under it.

Cap: $100 total across all runs, enforced by `cost_guard.py` (ledger in `ledger/`). It aborts the run when a call would pass the cap (tested with a fake local provider in `validate_cost_abort.py`, no network).
