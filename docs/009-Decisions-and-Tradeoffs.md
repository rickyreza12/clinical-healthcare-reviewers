# Decisions and Tradeoffs

| Decision | Reason | Alternative / tradeoff |
|---|---|---|
| Deterministic checks first | Identity, date, required fields, and known diagnosis mappings are directly testable against SOPs. | A general model might interpret more wording but adds variance and unsupported inference risk. |
| Optional narrow semantic fallback for unmapped diagnoses | Credentials now configure a self-hosted adapter with structured output, minimal input, bounded retries and usage records. Disabled, unavailable, malformed or explicitly contradictory results escalate. | Model format/connectivity are verified; clinical quality still requires evaluation. |
| Local file manifest and DOCX parsing | Matches supplied assessment package and keeps setup small. | A database/object store is needed for multi-user production operations. |
| Rule metadata for seven SOPs | Small, stable corpus is easy to load and inspect. | Hybrid/vector retrieval is a future option for a larger corpus, with retrieval evaluation. |
| Metadata is optional and distinct | Default response stays focused on the review result; debug data does not change finding meaning. | Internal production traces should be access controlled and may omit details from public responses. |
| Self-hosted cost is runtime allocation | Hourly rate multiplied by seconds / 3600 is reproducible for request allocation. | Idle capacity and shared infrastructure require separate allocation; this is not a provider invoice. |
