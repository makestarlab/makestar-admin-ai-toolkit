---
name: makestar-read-only-query
description: Fast routing skill for read-only Makestar admin queries using verified resource scripts.
version: 0.1.5
author: Makestar Admin Contracts
license: MIT
---

# Makestar Read-Only Query

Use this when the user asks to look something up in Makestar admin/OMS without changing data.

This is the thin operator-facing layer built on top of the broader `makestar-admin-resource-scripts` skill.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.6.
Before the first CLI-dependent action, run `makestar-admin --version`, compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Show the documented install path that can provide the required version for this platform, such as macOS `brew install makestarlab/tap/makestar-admin-cli`, Windows `winget install Makestar.MakestarAdminCLI` when current enough, or the public release MSI/archive; then stop until the user updates.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require source-checkout or Python-module fallback commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## Use when
- The user wants to find a B2B 업체, member, order activity, or deposit log.
- The user wants to inspect orders, purchase orders, purchase requests, ASN search results, inbounds, SKUs, or product events.
- You want a direct question -> command mapping with verified CLI flags.

## Do not use for
- create/update/delete flows
- vendor changes
- ASN create/delete
- deposit charge/deduct/confirm-payment
- any write endpoint, even if the request shape is known

## Preconditions
- You need a valid Makestar admin bearer token staged for the current session.
- If the shell token is stale or missing, load `makestar-admin-auth-token` first and stage tokens with the shell-appropriate Bash/Git Bash or PowerShell command from that skill.
- Fall back to `makestar-admin-browser-token` only when the Auth CLI path is unavailable or blocked.

## Default workflow
1. Map the user question to a verified command from `references/routes.md`.
2. Run only the smallest read-only CLI command needed.
3. If `/user-group/{id}` is involved, remember it is a composite page and split the read into detail / members / orders / deposit resources as needed.
4. Return screen-visible fields first, then related ids/keys.
5. If the needed filter is not exposed by the current CLI command, fall back to `makestar-admin-resource-scripts` and inspect the contract before inventing flags.

## Recommended answer shape
- Start with the user-visible answer first.
  - Example: company name, status, manager, order number, payment status, SKU name, balance.
- Then include the minimum useful related ids/keys.
  - Example: `group_id`, `order_no`, `purchase_order_code`, `purchase_order_request_id`, `sku_code`, `event_id`.
- When a visible enum/grade has an operator-facing label, prefer `raw(label)` form on first mention.
  - Example: `grade 0(E)`.
- If the page is composite, say so explicitly.
  - Example: `/user-group/{id}` is composed from detail, members, orders, balance, and deposit logs.
- If the result is empty, treat that as a valid read result, not a failure.
- If the script output contains both display fields and internal keys, summarize display fields first and keep internal keys in a short trailing block.
- For lists, prefer:
  1. filter summary
  2. total count
     - prefer server-side pagination/count when available
     - if the current script summary only exposes page row count, say that explicitly instead of implying global total
  3. top 3-10 rows in compact form
  4. related ids/keys only where operationally useful
- Count rule learned from live use:
  - prefer server-side pagination/count totals when available
  - do not present the current page row count as the overall total unless that is truly all the API returns
- For detail views, prefer:
  1. primary visible fields
  2. related object summaries
  3. supporting ids/keys
  4. contract nuance if important (for example OMS fallback, row-backed detail, composite page)

## Fast routes
- B2B 업체 찾기
  - `makestar-admin user-groups list --name-or-email <email> --size 10`
  - `makestar-admin user-groups list --company-name <company> --size 10`
  - `makestar-admin user-groups list --manager-name <manager> --size 10`
  - `makestar-admin user-groups list --country-code KR --size 10`
  - `makestar-admin user-groups list --has-offline-store True --size 10`
  - `makestar-admin user-groups list --user-group-grade 4 --user-group-grade 0 --size 10`
- B2B 업체 상세/활동
  - `makestar-admin user-groups detail <group_id> --include-balance`
  - `makestar-admin user-groups members list <group_id>`
  - `makestar-admin user-groups orders list <group_id>`
  - `makestar-admin user-groups deposit-logs list <group_id>`
  - `makestar-admin user-groups deposit-logs list <group_id> --log-type EARN`
  - `makestar-admin user-groups deposit-logs list <group_id> --start-date 2026-03-31 --end-date 2026-03-31`
- 주문
  - `makestar-admin orders list --size 10`
  - `makestar-admin orders list --b2b --size 10`
  - `makestar-admin orders list --product-event-code <event_code> --size 10`
  - `makestar-admin orders list --recipient-name <name> --size 10`
  - `makestar-admin orders list --shipping-status 0 --size 10`
  - `makestar-admin orders detail <order_no>`
- 구매/입고/ASN
  - `makestar-admin purchase-orders list --size 10`
  - `makestar-admin purchase-orders list --purchase-order-code <po_code> --size 10`
  - `makestar-admin purchase-orders list --vendor-id <vendor_id> --size 10`
  - `makestar-admin purchase-orders detail <purchase_order_code>`
  - `makestar-admin purchase-requests list --size 10`
  - `makestar-admin purchase-requests list --status REQUESTED --size 10`
  - `makestar-admin purchase-requests detail <purchase_order_request_id>`
  - `makestar-admin advance-ship-notices search --purchase-order-code <purchase_order_code>`
  - `makestar-admin inbounds detail --purchase-order-code <po_code> --goods-received-note-id <grn_id>`
- SKU/이벤트
  - `makestar-admin skus search --size 10`
  - `makestar-admin skus search --below-safety-quantity-only Y --size 10`
  - `makestar-admin skus search --vendor-id <vendor_id> --size 10`
  - `makestar-admin skus stock-detail <sku_code>`
  - `makestar-admin product-events latest --display-status displayed --size 10`
  - `makestar-admin product-events list-by-code --code <event_code>`
  - `makestar-admin product-events detail <event_id>`
  - `makestar-admin product-contents list <product_id>`

## Notes
- `/user-group/{id}` is not a single API. Treat it as a composite page.
- Deposit log detail currently reuses the deposit-log list row as the read model; do not assume a separate detail GET exists.
- Keep answers read-only even if related write boundaries are already documented elsewhere.
- Favor concise operator-style answers: visible fields first, ids second, contract nuance only when it changes interpretation.

## References
- `references/routes.md`
- `references/response-templates.md`

Use `references/routes.md` as the operator cheat sheet: it now includes Korean question examples next to the verified command routes.
Use `references/response-templates.md` when you want the answer itself to follow a stable operator-style shape.
