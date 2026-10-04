# Clinical Document Review Assistant

Local FastAPI service that checks the supplied synthetic DOCX case packages and reports source-backed findings for a human reviewer. It does not adjudicate claims.

## Requirements and run

Python 3.11 or newer is required. From this directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The supplied case documents and SOPs live in `apps/data/candidate_package`. Set `BITHEALTH_DATA_DIR` to override that directory. Diagnosis comparisons use explicit terminology mappings first. Optional self-hosted model fallback is configured through `apps/.env`, loaded automatically for local startup and injected by Compose. With `SEMANTIC_ENABLED=false`, no model key is required and unresolved comparisons are escalated.

`.env.example` is active Compose baseline configuration. Local Python startup does not require `.env`. Docker Compose requires it: on a fresh checkout, copy `.env.example` to `.env` (Windows: `Copy-Item .env.example .env`; macOS/Linux: `cp .env.example .env`). Keep `SEMANTIC_ENABLED=false` for a run without model credentials. Never overwrite an existing private `.env` or commit it. See [self-hosted integration guide](../workspaces/integration-with-api/self-hosted-model-integration.md) for model selection, usage records, cost accounting and verification.

See [self-hosted model guide](docs/012-Self-Hosted-Models.md) for the available model catalog, configuration, model switching, discovery command, and synthetic smoke check.

SOP source text is kept in `apps/data/candidate_package/policies_sops`. On the first Compose run, the one-shot `policy-indexer` embeds `apps/data/policy_chunks.jsonl` with local CPU FastEmbed and stores the vectors in Qdrant. It indexes SOP text only; it never indexes patient case documents. Persistent volumes retain both Qdrant data and downloaded embedding-model files. Re-run it after policy changes with `docker compose run --rm policy-indexer`.

Embedding and AI comparison are separate on purpose. FastEmbed supplies local SOP-search vectors because the current self-hosted model API does not implement `/embeddings`. Diagnosis semantic comparisons use `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` from private `.env`; Compose loads `.env.example` first, then uses `.env` as its override.

`SELF_HOSTED_HOURLY_USD` allocates monthly infrastructure cost over model-call wall-clock time. For IDR 150,000/month, use `0.01149` USD/hour when using Rp17,898/USD and 730 hours/month. This is allocation reporting, not a provider invoice.

## Documentation

Read the documents in this order:

1. [Requirements](docs/001-Requirement-Analysis.md)
2. [Non-goals](docs/002-Non-Goals.md)
3. [Review status](docs/003-Review-Status-Enum.md)
4. [Severity](docs/004-Severity-Enum.md)
5. [Finding codes](docs/005-Finding-Codes.md)
6. [API contract](docs/006-API-Contract.md)
7. [Architecture](docs/007-Architecture.md)
8. [Cost summary](docs/008-Cost-Summary.md)
9. [Decisions and tradeoffs](docs/009-Decisions-and-Tradeoffs.md)
10. [Submission checklist](docs/010-Final-Submission-Checklist.md)
11. [Production considerations](docs/011-Production-Considerations.md)
12. [Self-hosted models](docs/012-Self-Hosted-Models.md)

## Review a case

```bash
curl -X POST "http://127.0.0.1:8000/cases/CASE-010/review?include_metadata=true"
```

Use `CASE-001` through `CASE-010`. Success responses contain `review_status`, `requires_human_review`, findings, evidence, and SOP references. `include_metadata` defaults to false. See `/docs` for OpenAPI. `/health` is a liveness check.

## Tests

```bash
python -m pytest
```

## Docker

From the `apps` directory, create `.env` as described above, then start the API in the background with:

```bash
docker compose -f compose.yaml up --build -d clinical-review-api
```

Follow logs with `docker compose -f compose.yaml logs -f`, check first-run indexing with `docker compose logs policy-indexer`, and stop it with `docker compose -f compose.yaml down`. The API is available at `http://127.0.0.1:8000`; Compose reports the container health at `/health`. Qdrant uses a persistent named volume and stays on the internal Compose network (not published to the host). Its URL inside Compose is `http://qdrant:6333`.

The minimal API command above does not start Qdrant, the policy indexer, or Phoenix: deterministic case review does not depend on them. To start all optional services, run `docker compose -f compose.yaml up --build -d` instead. The first policy-indexer run requires internet access to download the embedding model. Its vectors are prepared for future retrieval and are not queried by current case reviews.

Phoenix is available at `http://127.0.0.1:6006` when `PHOENIX_ENABLED=true` in `.env`. It receives prompt-free model-call telemetry: model, token counts, latency, outcome, retry, and cost fields. See [Phoenix monitoring](../workspaces/integration-with-api/self-hosted-model-integration.md#phoenix-monitoring) for setup and limits.
