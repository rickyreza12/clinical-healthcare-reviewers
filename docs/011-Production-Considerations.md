# Production Considerations

- **Privacy and security:** authenticate and authorize reviewers, encrypt transport and storage, minimize PHI in logs, define retention/deletion rules, and threat-model malicious document content. Current sample data is synthetic and the demo has no authentication or persistence.
- **Reliability:** enforce upload and parser limits, isolate malformed files, add bounded timeouts, health/readiness checks, durable queues only if asynchronous scale is required, and monitor error rates and latency.
- **Auditability:** persist case/document references, content hashes, policy and rule versions, result, reviewer action, and trace ID in a controlled audit store. Current implementation is file-based input and does not retain review history.
- **Policy/model governance:** version each policy, validate rule changes against a regression suite, and require clinical/policy owner review. Any future model must be constrained, evaluated, monitored, and unable to decide claim outcomes.
- **Scaling:** evaluate concurrent DOCX parsing, request limits, and a durable work queue before adding infrastructure. Authoritative SOP selection is in-memory. Optional Qdrant contains SOP embeddings for future semantic retrieval; current case reviews do not query it.
- **Cost and service levels:** the local deterministic implementation has no inference cost. Establish actual service-level and hosted/self-hosted cost baselines before production commitments.
