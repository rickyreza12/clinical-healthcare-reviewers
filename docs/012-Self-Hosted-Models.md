# Self-hosted model guide

## Purpose

The Clinical Document Review Assistant uses a self-hosted, OpenAI-compatible chat API only for unresolved diagnosis comparisons. Deterministic checks run first. Model output is constrained to `equivalent`, `conflict`, `uncertain`, or `indeterminate`; invalid output and outages result in human review.

The bearer token belongs only in private `apps/.env`. Do not commit it, print it, or add it to requests in documentation.

## Configure a model

Create `apps/.env` from `.env.example`, then set the private values:

```dotenv
SEMANTIC_ENABLED=true
LLM_BASE_URL=http://ricky-selfhosted-ai.web.id
LLM_API_KEY=your-private-token
LLM_MODEL=QuantFactory/Qwen3-0.6B-GGUF:Q4_K_M
LLM_TIMEOUT_SECONDS=60
```

`LLM_BASE_URL` must not include `/models` or `/chat/completions`. Docker Compose loads `.env.example` first and applies `.env` after it, so private values override the safe defaults.

## Available models

The sanitized discovery catalog in `apps/data/model_catalog.json` lists these models:

| Model ID | Input | Notes |
|---|---|---|
| `QuantFactory/Qwen3-0.6B-GGUF:Q4_K_M` | Text | Current configured development model. |
| `bartowski/google_medgemma-4b-it-GGUF:Q4_K_M` | Text, image | Current adapter submits text only. |
| `biomistral-7b` | Text | Requires live validation before use. |
| `llama3.2-medical-1b` | Text | Requires live validation before use. |
| `llama3.2-medical-3b` | Text | Requires live validation before use. |
| `medgemma-4b` | Text | Requires live validation before use. |
| `meditron-7b` | Text | Requires live validation before use. |
| `phi3-mini-medical` | Text | Requires live validation before use. |
| `qwen25-medical-1.5b` | Text | Requires live validation before use. |

Presence in discovery means the router knows the model ID. It does not prove the model can load, return schema-valid JSON, or make clinically reliable judgments.

## List current server models

From `apps`, list model IDs without exposing credentials or server paths:

```powershell
python -m backend.semantic.discover_models
```

For the Compose container:

```powershell
docker compose exec -T clinical-review-api python -m backend.semantic.discover_models
```

The command calls the authenticated `/models` endpoint and prints model IDs only.

## Switch a model

1. Change `LLM_MODEL` in private `.env` to an exact model ID from discovery.
2. Recreate the API so Compose loads the new environment value.
3. Run the synthetic smoke check.

```powershell
docker compose up -d --force-recreate clinical-review-api
docker compose exec -T clinical-review-api python -m backend.semantic.smoke
```

The smoke check sends only synthetic diagnosis strings. It records model, token counts, latency, retry count, outcome, and cost; it does not record prompts, diagnoses, rationale, patient data, or credentials in telemetry.

Use a model only after it returns schema-valid output consistently for reviewed test cases. It supports human review; it does not approve, deny, or adjudicate claims.

## Embeddings are separate

The current self-hosted API returns `501 Not Implemented` for `/embeddings`. Qdrant therefore uses local CPU FastEmbed model `BAAI/bge-small-en-v1.5` for SOP-only vectors. It creates 384-dimensional vectors and never embeds case documents. See [README](../README.md) for first-run indexing.

When the self-hosted server provides an OpenAI-compatible embedding endpoint and an embedding-capable model, configure and validate that provider separately before replacing FastEmbed.
