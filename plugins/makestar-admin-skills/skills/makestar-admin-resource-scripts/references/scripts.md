Usage pattern notes:
- Start from the question pattern examples in `SKILL.md` or `references/question-patterns.md`.
- As of the 2026-04-18 CLI help audit, the documented examples for grade filtering, order event-code filtering, and B2B order filtering are aligned to actual script flags.
- Stay read-only: query scripts are allowed; create/update/delete are not.
- If a requested filter is not exposed by the current script CLI, inspect the script help or resource contract before inventing flags.
- For B2B `/user-group/{id}` questions, remember the page is composite: detail, members, orders, deposit balance, and deposit logs are separate reads.
- For deposit log detail questions, use the logs list row as the read model; do not assume a separate detail GET exists.
