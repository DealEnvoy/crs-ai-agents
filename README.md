# Certificate of Release to Service (CRS) for AI agents, Pilot 0

Repository `crs-ai-agents` (earlier working title: *Release Gate Pilot 0*).

**CRS for AI agents, Pilot 0** applies the idea of a *Certificate of Release to Service* (CRS) to AI agents. In aircraft maintenance, a person signs to say finished work is fit to release, after checking that the work pack's own records support that statement. Pilot 0 asks a narrower question: can an AI model act as an **advisory reviewer** of a finished work pack (never the one who signs) and notice when the pack's own evidence does not support its "done" statements?

This is a small, pre-registered pilot. It is not a product, a certification tool or a validated safety method.

## What was tested

- **Tasks.** 8 tasks, each with two packs: a **faulty** pack with exactly one seeded fault, and a **clean twin** with no fault. 16 packs in total.
  - 5 aviation-style tasks (A1 missing sign-off, A2 independent inspection missing, A3 value outside limit, A5 deferred defect beyond limit, A8 airworthiness directive overdue). The work packs are invented, with fictional aircraft and registrations. The fault patterns are inspired by public UK AAIB reports (listed in `aviation_tasks/README.md`).
  - 3 software tasks (S1 to S3), derived from one small software project's own deploy log, with names, phone numbers, emails and customer data replaced by placeholders. The closure requests and the 8-line gate draft in each pack are written for the evaluation, not taken from the log (`software_tasks/README.md`).
- **Reviewer output.** One JSON object: findings (category, location id, exact quote, explanation), claims with evidence references, and a recommendation of `HOLD_FOR_HUMAN` or `NO_FINDINGS_FOR_HUMAN_REVIEW`. The reviewer is told it must never state that an aircraft is released, serviceable or airworthy, or that a ticket is done or approved.
- **Models under test.** `claude-fable-5-1`, `gpt-6-astra`, `gemini-4-argon`, each with provider-default sampling, `max_tokens` 4000 (including hidden reasoning), 2 epochs per pack. Built on [Inspect](https://inspect.aisi.org.uk/) (`crs_pilot.py`).
- **Scoring is by code.** Detection, localisation (right location id), exact-quote evidence match, false alarms on clean twins, invented quotes (a finding whose quote is not a verbatim substring of the pack) and forbidden "released / safe to close" language are all computed by code. Counts are reported with **Wilson 95% intervals**; there are no significance tests and no ranking of models.
- **Cross-provider grading.** A secondary metric ("do the findings identify the seeded problem?") is model-graded, and **no model grades its own provider**: Claude is graded by GPT, GPT by Gemini, Gemini by Claude. The harness asserts this in code. The grader never changes a primary metric.
- **Pre-registered rules.** `SCORING_RULES.md` fixes the metrics, aggregation and threats to validity. File hashes are in `PREREG_HASHES*.txt`; `python3 verify_prereg.py` checks them (see "Pre-registration integrity" below).
- **Hard cost cap.** `cost_guard.py` enforces a **$100 hard cap** across all runs. Each call reserves its worst-case cost first and is refused if spent plus reserved plus that call would pass the cap. The cap can be lowered by environment variable, never raised. Calls are logged to `ledger/calls.jsonl`.

## Results

All numbers below are from the files in this repo (`results/`, `results/v2/`, `ledger/`) and can be regenerated from the included Inspect logs with `analyse_results.py` and `spend_report.py`.

Totals: **309 model calls (195 reviewer, 114 grader) plus 1 logged cost correction = 310 ledger rows; $11.79 total spend** (list-price estimate from reported token usage; an upper bound on invoices), against the $100 cap.

### Run 1 (pre-registered task set, "v1")

| Measure, per model (16 faulty and 16 clean task-epochs) | claude-fable-5-1 | gpt-6-astra | gemini-4-argon |
|---|---|---|---|
| Seeded faults caught (`HOLD_FOR_HUMAN`) | 16 / 16 (CI 0.81 to 1.00) | 16 / 16 (CI 0.81 to 1.00) | 16 / 16 (CI 0.81 to 1.00) |
| ...with right location id and exact-quote evidence | 16 / 16 | 16 / 16 | 16 / 16 |
| False alarms on clean twins | 8 / 16 (CI 0.28 to 0.72) | 6 / 16 (CI 0.18 to 0.61) | 8 / 16 (CI 0.28 to 0.72) |
| Invented or non-exact quotes | 0 / 117 findings | 0 / 46 findings | 0 / 54 findings |
| Forbidden-language hits (replies) | 0 / 32 | 0 / 32 | 0 / 32 |

False alarms split by domain in run 1: aviation 2 / 10 for every model (all from the clean twin of A8), software 6 / 6, 4 / 6 and 6 / 6. Hand-reading showed design flaws in the clean twins of A8, S2 and S3 (and an ambiguity in S1). The pre-registered rule still counts them as false alarms, and they are reported that way.

### Run 2 ("v2": repaired clean twins, exploratory)

After run 1, the clean twins of A8, S1, S2 and S3 were repaired (the 8 faulty packs are byte-identical) and all three models were run again with the same prompts and scorer. v2 is a **post-hoc repair designed after seeing run 1**; it is reported next to run 1, not instead of it. Changes are listed in `SCORING_RULES.md` (changelog "v2") and `results/v2/RESULTS.md`.

| Measure, per model | claude-fable-5-1 | gpt-6-astra | gemini-4-argon |
|---|---|---|---|
| Seeded faults caught | 16 / 16 (CI 0.81 to 1.00) | 16 / 16 (CI 0.81 to 1.00) | 16 / 16 (CI 0.81 to 1.00) |
| ...with right location id and exact-quote evidence | 16 / 16 | 16 / 16 | 16 / 16 |
| False alarms on clean twins | 6 / 16 (CI 0.18 to 0.61) | 3 / 16 (CI 0.07 to 0.43) | 4 / 16 (CI 0.10 to 0.49) |
| Invented or non-exact quotes | 0 / 99 findings | 0 / 38 findings | 0 / 45 findings |
| Forbidden-language hits (replies) | 2 / 32 (see note) | 0 / 32 | 0 / 32 |

- **Aviation tasks: 0 / 10 false alarms for every model in v2** (in run 1 it was 2 / 10 each, caused by the flawed A8 twin). Software false alarms remain: 6 / 6, 3 / 6 and 4 / 6.
- The 2 forbidden-language hits for Claude are quotations of the pack's own wording inside an explanation or claims note. They are counted as hits because the registered rule only removes the verbatim finding quotes before matching.
- Tasks A1, A2, A3 and A5 (twins unchanged) had no false alarms for any model in either run. Run 1 was not repeated unchanged, so differences on the repaired twins cannot be separated from sampling noise.

### How to read this

- All three models caught every seeded fault, located it and quoted the evidence exactly. With 16 trials the Wilson lower bound for "always catches it" is 0.81, so this means "no misses seen", not "never misses".
- The faulty packs put the contradicting line on the page. This is a reading-comprehension test, not a test of predicting a failure.
- Detection of 100% alongside false alarms of 19% to 50% means these reviewers lean cautious. A reviewer that held every pack would score the same on detection, so the false-alarm column is the informative one. Most remaining false alarms are on software packs that lack test-to-claim mapping; they are better read as "asked for more evidence" than as hallucination. No quote was ever invented.
- Gemini 4 Argon was run about 50 minutes after the other two models in run 1 (the first attempt failed with an HTTP 429 quota error, nothing billed, and it was repeated once billing was enabled). Until then GPT's findings were graded by Claude; they were then also graded by Gemini, the registered grader. Both gave 16 / 16 "yes". Details in `SCORING_RULES.md`.

### Spend summary

From `ledger/calls.jsonl` (`python3 spend_report.py` regenerates `results/spend_all.json`). Token counts are as logged by the ledger; Anthropic input tokens include cache writes at 1.25x and cache reads at 1.0x.

| Provider (model) | Calls | Input tokens | Output tokens | Cost (USD) |
|---|---|---|---|---|
| Anthropic (claude-fable-5-1) | 114 | 195,196 | 123,728 | 8.1384 |
| OpenAI (gpt-6-astra) | 98 | 126,013 | 33,854 | 2.9528 |
| Google (gemini-4-argon) | 97 | 118,156 | 42,490 | 0.6612 |
| Logged cost correction (Anthropic smoke test, cache-write tokens first missed by the accounting) | n/a | n/a | n/a | 0.0328 |
| **Total** | **309** | **439,365** | **200,072** | **11.7852** |

By phase: run 1 $6.1163, run 2 $5.6688 (`results/spend.json`, `results/v2/spend.json`). List prices used: $10 in / $50 out per million tokens for Claude and GPT; $2 in / $10 out for Gemini (valid until 2026-11-30 in `cost_guard.py`).

The ledger holds only timestamp, model name, token counts, cost, running total and a short tag such as `solver:A1-faulty` or `grader`. It contains no prompts, keys or account identifiers.

## Limits

- **Small sample.** 16 faulty and 16 clean task-epochs per model (8 tasks x 2 epochs). Epochs are repeats of the same pack, not independent samples. Intervals are wide.
- **Invented aviation tasks.** The aviation packs are fictional work packs. They are inspired by the *kind* of failure in public AAIB reports and do not reproduce those reports' facts. No real operator records or aircraft records are used.
- **Software packs** come from one project, with harness-written closure requests and gate drafts. Some "clean" lines are counterfactual (an outcome that did not happen).
- **Review-only.** The model reviews a finished pack and advises. It does not decide, release, repair or sign anything.
- **Not validated in aviation.** Nothing here shows that this approach is safe or suitable for any real maintenance, release or regulatory process.
- **Twin quality matters.** Run 1 false-alarm numbers were partly a measure of flawed clean twins. v2 repaired some flaws after seeing the results; residual strictness remains, so software false-alarm rates are probably an upper bound on genuine over-flagging.
- One prompt per domain, no prompt tuning, provider-default sampling, 4,000-token output cap. Other prompts or settings may behave differently.
- Cost figures are list-price estimates, not invoices.
- No claim is made of any partnership, endorsement, regulatory acceptance or compliance with any standard or regulation.

## Reproduce

Python 3.13 was used.

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.lock.txt

# Free checks, no provider calls (keys must be unset)
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u GOOGLE_API_KEY .venv/bin/python validate_mock.py
env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u GOOGLE_API_KEY .venv/bin/python validate_cost_abort.py

# Re-score the included Inspect logs (no model calls); regenerates results/ byte-for-byte
.venv/bin/python analyse_results.py v1
.venv/bin/python analyse_results.py v2
.venv/bin/python spend_report.py
.venv/bin/python make_tables.py
.venv/bin/python verify_prereg.py
```

To repeat the real runs you need your own provider keys. Real calls are refused unless `CRS_REAL_RUN_APPROVED=YES` is set. The ledger in `ledger/` is the live spend state for the cap, so move it aside to start a separate budget:

```
CRS_REAL_RUN_APPROVED=YES .venv/bin/inspect eval crs_pilot.py \
  --model anthropic/claude-fable-5-1,openai/gpt-6-astra,google/gemini-4-argon \
  --max-connections 4 --max-samples 4 --log-dir logs/my_run
# v2 task set:  CRS_TASK_ROOT=v2 ... (same command)
```

## Repository layout

| Path | What it is |
|---|---|
| `crs_pilot.py` | Inspect task, prompts, scorer, grader map |
| `cost_guard.py` | $100 hard cap, price table, per-call ledger |
| `SCORING_RULES.md`, `PREREG_HASHES*.txt`, `verify_prereg.py` | Pre-registered rules, hashes, hash checker |
| `WORDING_EDITS.md`, `wording_edits.json`, `verify_wording_edits.py` | Record and check of the one edit made to a hash-listed file after the runs |
| `aviation_tasks/`, `software_tasks/` | Run 1 task packs, answer keys, builders, prompt templates; links to the AAIB reports and the short quotes relied on (full report texts are not included) |
| `v2/` | Run 2 task set (repaired clean twins), built by `build_v2.py` |
| `results/`, `results/v2/` | Per-sample data, tables, charts, written results for each run |
| `logs/real_run_1/`, `logs/real_run_2/` | Inspect logs of the real runs (reviewer and grader replies) |
| `logs/mock_validation/summary.json` | Summary of the free scorer validation |
| `ledger/calls.jsonl`, `ledger/spend.json` | Full per-call spend ledger and running total |
| `COST_ESTIMATE.md`, `estimate_cost.py`, `cost_estimate.json` | Pre-run cost estimate |
| `analyse_results.py`, `make_report.py`, `make_tables.py`, `regrade_gpt_with_argon.py`, `spend_report.py` | Analysis scripts |

The failed first Gemini attempt in run 1 (HTTP 429 quota error, nothing billed), the smoke-test logs and the mock-validation logs are not included. The source project for the software packs is not included; `software_tasks/build_software_packs.py` and `verify_provenance.py` need it (path in `TBC_REPO`), and the packs and provenance tables are included instead.

## Pre-registration integrity

`PREREG_HASHES.txt` was written before any real call; `PREREG_HASHES_v2.txt` before any v2 call. All 39 files in the v2 list match. Differences against the run 1 list are expected and recorded: `crs_pilot.py`, `cost_guard.py` and `SCORING_RULES.md` were edited after registration (changelog in `SCORING_RULES.md`: cost accounting fix, grader override hook, v2 task-root switch). `software_tasks/build_software_packs.py` was edited after the runs to move a local path and redaction terms out of the published script; it does not affect the hashed packs. The hash lists themselves are unchanged. `WORDING_EDITS.md` records that edit, and `verify_wording_edits.py` rebuilds the original by reversing it and compares it with the recorded digest (this needs a private file holding the removed text, which is not published). `python3 verify_prereg.py` lists every difference.

## Sources and licence

- Code: MIT, see `LICENSE` (copyright Isaac Adekunle). The `LICENSE` file also covers the other original material in this repository (synthetic task packs, answer keys, results); third-party material is excluded.
- AAIB reports: the full report texts are **not** included. `aviation_tasks/aaib_sources.json` gives links to the official AAIB report pages and PDFs, plus the short quotes the task notes rely on (`python3 aviation_tasks/verify_sources.py --fetch` checks each quote against the official PDF). AAIB extracts and quotes remain under the publishers' terms (the reports are published under the UK Open Government Licence v3.0) and are not covered by the MIT licence.
- `aviation_tasks/source_notes/regulation_excerpts.txt` holds short extracts of UK Regulation (EU) No 1321/2014 (CAA consolidation, CAA regulatory library). They are third-party material under the publisher's terms and are not covered by the MIT licence.
