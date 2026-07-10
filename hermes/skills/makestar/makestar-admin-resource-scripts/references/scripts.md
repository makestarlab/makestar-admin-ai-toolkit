Usage pattern notes:
- Start from the question pattern examples in `SKILL.md` or `references/question-patterns.md`.
- As of the 2026-04-18 CLI help audit, the documented examples for grade filtering, order event-code filtering, and B2B order filtering are aligned to actual script flags.
- Stay read-only: query scripts are allowed; create/update/delete are not.
- If a requested filter is not exposed by the current script CLI, inspect the script help or resource contract before inventing flags.
- For `skus search`, `safetyQuantity` is 안전재고 and `vendorPackSize` is 박스당 수량; keep both visible and separate in operator summaries.
- For `skus stock-detail`, distributor deadline fields are detail-only: `distributorPreOrderDeadline` is 유통사 선주문 발주 마감일 and `distributorFinalOrderDeadline` is 유통사 최종 발주 마감일.
- For B2B `/user-group/{id}` questions, remember the page is composite: detail, members, orders, deposit balance, and deposit logs are separate reads.
- For deposit log detail questions, use the logs list row as the read model; do not assume a separate detail GET exists.
