# API Contract

The service uses `POST /cases/{case_id}/review` because review runs document processing and returns a structured result; the case ID in the path selects exactly one manifest bundle. `include_metadata=true` opts into execution metadata. There are no arbitrary model or policy selectors.

Responses use a shared `ReviewResponse`: case ID, `clear`/`needs_review`, human-review flag, findings, and optional metadata. Findings contain a stable type, severity, description, source evidence, SOP reference, and human-review reason. A successful `needs_review` is still HTTP 200. Unknown cases return 404; invalid requests return 422; unreadable source documents return a safe 422 Problem Details response; unexpected failures return a generic 500 problem with a trace ID.
