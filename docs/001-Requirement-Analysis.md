# Requirement Analysis

## Supplied requirements

The technical test requests an API that accepts or identifies one supplied patient case and returns a structured JSON review. It must identify missing records or fields, compare identity and dates, check diagnoses, consult the provided SOPs, and return findings with evidence. The supplied package requires architecture documentation with a valid Mermaid diagram, a per-call LLM cost record, aggregate costs, and reproducible setup instructions. Human review remains necessary where evidence is uncertain or incomplete.

## Ambiguities

- The assignment does not prescribe exact API field names, HTTP methods, severity values, or review-status values.
- It does not define broad clinical equivalence beyond the supplied SOP examples.
- It does not provide hosted model prices or a production target for latency, throughput, or retention.
- One workspace story-style explanation describes CASE-007 as missing a discharge summary, while the supplied manifest contains that summary and the candidate walkthrough/task acceptance identify invalid chronology. The source documents and deterministic task acceptance are used as the executable truth.

## Implementation assumptions

- The case identifier is in `POST /cases/{case_id}/review`; optional processing metadata is a query parameter.
- Status values are `clear` and `needs_review`; API failures use Problem Details responses.
- Explicit terminology mappings handle known equivalents. Unresolved diagnoses defer to a reviewer; no external model is needed for local operation.
- Supplied DOCX paths are read from the candidate package and no case data is persisted.

## Scope and non-goals

The service validates only rules grounded in SOP-01 through SOP-07 and the supplied task acceptance criteria. It does not approve, deny, or reject claims or provide medical diagnoses. See [002-Non-Goals.md](002-Non-Goals.md).

## Success criteria

The API runs locally; all ten supplied acceptance cases return expected results; findings include source evidence and policy; missing source facts are not inferred; errors are distinct from review findings; deterministic paths have no model cost; setup and architecture/cost documentation are reproducible.
