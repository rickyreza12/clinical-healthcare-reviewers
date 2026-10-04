# Severity Enum

Severity applies to workflow findings, not patient condition or claim outcome. Exact values are an implementation assumption.

| Value | Deterministic mapping |
|---|---|
| `low` | Informational data-quality issue (reserved; current mandatory checks do not emit it). |
| `medium` | Missing required field/document, unsigned claim, or incomplete report section. |
| `high` | Identity mismatch, invalid chronology, out-of-stay procedure, diagnosis conflict/uncertainty, or missing required procedure report. |

Rules use the mappings declared alongside the check in `backend/review/service.py`; values are constrained by the `Severity` enum.
