# Review Status Enum

The exact enum is an implementation assumption; the source SOP requires an explicit human-review outcome and prohibits autonomous decisions.

| Value | Definition |
|---|---|
| `clear` | Processing completed and no supported review finding was identified. This is not claim approval. |
| `needs_review` | One or more supported issues or unresolved evidence questions require a human. This is not denial. |

Technical failures use HTTP errors and do not become clinical review statuses.
