# LLM Usage and Cost Summary

## Current self-hosted integration

Optional remote diagnosis comparison records server token counts, measured latency, failures, retries and self-hosted allocation estimates. Private `.env` sets `SELF_HOSTED_HOURLY_USD=0.01149`, derived from an IDR 150,000 monthly service cost. Usage is persisted in a prompt-free JSONL journal, with per-case and overall reporting. See the [runbook](013-Runbook.md#use-and-monitor-the-self-hosted-model). The tables below describe the original deterministic acceptance run; all ten supplied cases still make zero model calls.

## Pricing and calculation

The delivered implementation uses a local deterministic/mock path and makes zero hosted LLM calls for CASE-001 through CASE-010. Therefore, no provider pricing source applies to this run and actual LLM usage cost is USD 0.00. For hosted inference, use the selected model provider's official published pricing page, record that URL and its effective date in the `TokenPrice` snapshot, and calculate `(input_tokens × input_USD_per_million + output_tokens × output_USD_per_million) / 1,000,000`; see `backend/cost/hosted.py`. Prices must be refreshed when provider/model configuration changes. No unsourced current price is asserted here.

## Per-call records

No LLM calls were made in the deterministic acceptance run; consequently that run has zero call rows. The remote provider uses the `LLMCall` schema and `aggregate_by_case` to report each call's provider/runtime/model, tokens, latency, retries, cache state, outcome, and cost. Executed integration calls are listed separately below. Local deterministic diagnosis rules are not model calls.

## Totals by supplied case

| Case | Calls | Input tokens | Output tokens | LLM cost USD | Latency ms |
|---|---:|---:|---:|---:|---:|
| CASE-001 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-002 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-003 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-004 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-005 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-006 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-007 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-008 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-009 | 0 | 0 | 0 | 0.000000 | 0 |
| CASE-010 | 0 | 0 | 0 | 0.000000 | 0 |

| Overall calls | Input tokens | Output tokens | LLM cost USD |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0.000000 |

## Recorded remote integration calls

The local prompt-free journal contains the following two executed integration calls, recovered during the submission audit on 2026-10-04. These are separate from the ten supplied deterministic acceptance cases. Both used provider `llama.cpp_compatible`, runtime `self_hosted`, model `QuantFactory/Qwen3-0.6B-GGUF:Q4_K_M`. The hourly allocation rate was not configured when these calls ran; recorded costs are **unknown**, not zero. No hosted per-token price applies to this self-hosted run.

| Call ID | Case | Input tokens | Output tokens | Latency ms | Retries | Cache | Outcome | Recorded cost USD |
|---|---|---:|---:|---:|---:|---|---|---|
| 543c51a043d34a738859861325cec3fa | INTEGRATION-SMOKE | 332 | 83 | 8085.9894 | 0 | not_used | uncertain | unknown |
| f1c45df71d474f198dab4b7d653bf208 | CASE-900 | 332 | 64 | 6139.7519 | 0 | not_used | conflict | unknown |

| Case | Calls | Input tokens | Output tokens | Latency ms | Recorded cost USD |
|---|---:|---:|---:|---:|---|
| INTEGRATION-SMOKE | 1 | 332 | 83 | 8085.9894 | unknown |
| CASE-900 | 1 | 332 | 64 | 6139.7519 | unknown |
| Overall integration calls | 2 | 664 | 147 | 14225.7413 | unknown |

Across supplied acceptance cases and these integration calls: 2 calls, 664 input tokens, 147 output tokens; total recorded inference cost remains unknown. The journal is excluded from Git and Docker build context; this table preserves recovered usage records without prompts or credentials.

### Allocation method

Allocated inference cost is `hourly infrastructure rate × measured runtime seconds / 3600`. Cost configuration uses `IDR 150,000 / Rp17,898 per USD / 730 hours = USD 0.01149/hour`. A 12-second call costs approximately USD 0.0000383, or IDR 0.6855. A projection supplied without executed inference is marked `is_estimate=true` by `backend/cost/self_hosted.py`. Per-request allocation excludes idle, always-on capacity; whole-period infrastructure bills should be reported separately to avoid presenting a runtime allocation as total spend.
