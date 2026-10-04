# Clinical Document Review Assistant

Local FastAPI service for reviewing supplied synthetic clinical document packages. It produces source-backed findings for a human reviewer. It does not approve, deny, or adjudicate claims.

## Start here

For the complete setup, operations, model, monitoring, and troubleshooting guide, read the [runbook](docs/013-Runbook.md).

## Quick start with Docker

Run these commands from this repository root:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Wait until `clinical-review-api` is `healthy`. The first run also starts Qdrant, indexes SOP chunks, and starts Phoenix.

Verify the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
curl.exe -X POST "http://127.0.0.1:8000/cases/CASE-010/review?include_metadata=true"
```

Open these URLs:

| Service | Address |
|---|---|
| API documentation | http://127.0.0.1:8000/docs |
| API health | http://127.0.0.1:8000/health |
| Phoenix monitoring | http://127.0.0.1:6006 |

`policy-indexer` completes and exits with code `0` after indexing 28 SOP chunks. This is expected.

## Configure self-hosted AI

The default `.env` runs deterministic review without model credentials. To enable semantic fallback, set these values in your private `.env`:

```dotenv
SEMANTIC_ENABLED=true
LLM_BASE_URL=http://your-model-host
LLM_API_KEY=your-private-token
LLM_MODEL=your-exact-model-id
SELF_HOSTED_HOURLY_USD=0.01149
```

Never commit or email `.env` or its bearer token. See [self-hosted models](docs/012-Self-Hosted-Models.md) for available models, discovery, switching, and smoke testing.

FastEmbed creates local 384-dimensional vectors for SOP-only Qdrant indexing. The self-hosted model API handles unresolved diagnosis comparisons. Patient documents are never embedded.

## Daily commands

```powershell
# Run tests
python -m pytest -q

# Follow API logs
docker compose logs -f clinical-review-api

# Rebuild the SOP index after editing policy_chunks.jsonl
docker compose run --rm policy-indexer

# Stop services
docker compose down
```

Run `docker compose down -v` only when you want to delete local Qdrant, Phoenix, telemetry, and embedding-cache volumes.

## Local Python development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Documentation

| # | Document |
|---:|---|
| 1 | [Requirements](docs/001-Requirement-Analysis.md) |
| 2 | [Non-goals](docs/002-Non-Goals.md) |
| 3 | [Review status](docs/003-Review-Status-Enum.md) |
| 4 | [Severity](docs/004-Severity-Enum.md) |
| 5 | [Finding codes](docs/005-Finding-Codes.md) |
| 6 | [API contract](docs/006-API-Contract.md) |
| 7 | [Architecture](docs/007-Architecture.md) |
| 8 | [Cost summary](docs/008-Cost-Summary.md) |
| 9 | [Decisions and tradeoffs](docs/009-Decisions-and-Tradeoffs.md) |
| 10 | [Submission checklist](docs/010-Final-Submission-Checklist.md) |
| 11 | [Production considerations](docs/011-Production-Considerations.md) |
| 12 | [Self-hosted models](docs/012-Self-Hosted-Models.md) |
| 13 | [Runbook](docs/013-Runbook.md) |
