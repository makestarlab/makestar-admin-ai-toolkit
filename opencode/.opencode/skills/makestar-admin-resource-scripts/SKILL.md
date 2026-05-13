---
name: makestar-admin-resource-scripts
description: Run Makestar admin low-level resource scripts consistently across admin and OMS paths.
version: 0.2.3
author: Makestar Admin Contracts
license: MIT
---

# Makestar Admin Resource Scripts

Use this skill to run the low-level resource probes without inventing new request shapes.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.6.
Before the first CLI-dependent action, run `makestar-admin --version`, compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Show the documented install path that can provide the required version for this platform, such as macOS `brew install makestarlab/tap/makestar-admin-cli`, Windows `winget install Makestar.MakestarAdminCLI` when current enough, or the public release MSI/archive; then stop until the user updates.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require source-checkout or Python-module fallback commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## Rules
- Prefer browser-confirmed request shapes.
- Keep admin and OMS resource families separate.
- If response meaning is unclear, inspect frontend first.
- Resource-level output should expose all information actually visible on the corresponding integrated-admin screen by default.
- If a page is composed from multiple connected resources, keep the single-resource script focused and express the combined screen in a composite/page-level skill or contract.
- Use this skill for read-only querying only. Do not use it for create/update/delete flows.
- If a write boundary exists but the task is still read-only, document the boundary source-only and stop there.

## Token setup
- Preferred current-session setup starts with shell-neutral login/status commands:
  - `makestar-admin auth status`
  - `makestar-admin auth login`
- Stage tokens in the current terminal only, matching the shell the agent is actually using. Git for Windows provides Git Bash, but Windows Claude/Codex sessions may run PowerShell.
  - macOS / Linux / Git Bash: `eval "$(makestar-admin auth token --shell)"`
  - Windows PowerShell:
    ```powershell
    $tokens = makestar-admin auth token --json | ConvertFrom-Json
    $env:MAKESTAR_ADMIN_ADMIN_TOKEN = $tokens.MAKESTAR_ADMIN_ADMIN_TOKEN
    $env:MAKESTAR_ADMIN_OMS_TOKEN = $tokens.MAKESTAR_ADMIN_OMS_TOKEN
    ```
  - Plain `cmd.exe` is not recommended; prefer PowerShell or Git Bash.
- These setup paths populate the env-token contract expected by resource scripts:
  - `MAKESTAR_ADMIN_ADMIN_TOKEN`
  - `MAKESTAR_ADMIN_OMS_TOKEN`
- If `makestar-admin auth` is not logged in or unavailable, load `makestar-admin-auth-token` for login/status/token handling first.
- Use `makestar-admin-browser-token` only as the fallback when CLI token acquisition is unavailable or blocked.
- Do not move login, refresh-token storage, or browser inspection logic into individual resource scripts; keep them env-token based and independently testable.

## Typical commands
- `makestar-admin product-events latest --display-status displayed --size 10`
- `makestar-admin product-events list-by-code --code <event_code>`
- `makestar-admin product-events detail <event_id>`
- `makestar-admin product-contents list <product_id>`
- `makestar-admin skus search --size 10`
- `makestar-admin skus stock-detail <sku_code>`
  - pricing questions should be answerable directly from the default summary output
  - summary should include at least `price`, `purchasePrice`, `taxationYn`, `vendorName`, `productionCompanyName`
- `makestar-admin orders list --size 10`
- `makestar-admin orders detail <order_no>`
- `makestar-admin orders get --ids <order_no1>,<order_no2>`
- `makestar-admin purchase-orders list --size 10`
- `makestar-admin purchase-orders detail <purchase_order_code>`
- `makestar-admin purchase-requests list --size 10`
- `makestar-admin purchase-requests detail <purchase_order_request_id>`
- `makestar-admin advance-ship-notices search --purchase-order-code <purchase_order_code>`
- `makestar-admin inbounds list --size 10`
- `makestar-admin inbounds detail --purchase-order-code <po_code> --goods-received-note-id <grn_id>`
- `makestar-admin user-groups list --size 10`
- `makestar-admin user-groups detail <group_id> --include-balance`
- `makestar-admin user-groups members list <group_id>`
- `makestar-admin user-groups orders list <group_id>`
- `makestar-admin user-groups deposit-logs list <group_id>`

## Question patterns -> commands

### B2B 업체/담당자 찾기
- "대표 이메일로 B2B 업체 찾기"
  - `makestar-admin user-groups list --name-or-email jinroh78@gmail.com --size 10`
- "업체명으로 B2B 업체 찾기"
  - `makestar-admin user-groups list --company-name 다이브원 --size 10`
- "담당자 이름으로 업체 찾기"
  - `makestar-admin user-groups list --manager-name 이재원 --size 10`
- "오프라인 매장 있는 B2B 업체만"
  - `makestar-admin user-groups list --has-offline-store True --size 10`
- "등급 A 또는 E 업체만"
  - `makestar-admin user-groups list --user-group-grade 4 --user-group-grade 0 --size 10`

### B2B 업체 상세 / 페이지 분해 조회
- "업체 484 상세 보여줘"
  - `makestar-admin user-groups detail 484 --include-balance`
- "업체 484 멤버 목록"
  - `makestar-admin user-groups members list 484`
- "업체 478 주문 활동"
  - `makestar-admin user-groups orders list 478`
- "업체 477 예치금 로그"
  - `makestar-admin user-groups deposit-logs list 477`
- "업체 477 예치금 EARN만"
  - `makestar-admin user-groups deposit-logs list 477 --log-type EARN`
- "업체 477 예치금 로그를 2026-03-31 하루만"
  - `makestar-admin user-groups deposit-logs list 477 --start-date 2026-03-31 --end-date 2026-03-31`

### 주문 조회
- "최근 주문 10개"
  - `makestar-admin orders list --size 10`
- "주문번호 C260418201844345M1 상세"
  - `makestar-admin orders detail C260418201844345M1`
- "특정 이벤트 코드 주문만 보고 싶다"
  - `makestar-admin orders list --product-event-code P_10103_BBGIRLS_3 --size 10`
- "B2B 주문 쪽을 보고 싶다"
  - `makestar-admin orders list --b2b --size 10`

### 구매 / 입고 / ASN 조회
- "최근 발주 10개"
  - `makestar-admin purchase-orders list --size 10`
- "발주서 PO 코드 상세"
  - `makestar-admin purchase-orders detail <purchase_order_code>`
- "구매요청 목록"
  - `makestar-admin purchase-requests list --size 10`
- "구매요청 상세"
  - `makestar-admin purchase-requests detail <purchase_order_request_id>`
- "특정 발주에 연결된 ASN 찾기"
  - `makestar-admin advance-ship-notices search --purchase-order-code <purchase_order_code>`
- "입고 상세 보기"
  - `makestar-admin inbounds detail --purchase-order-code <po_code> --goods-received-note-id <grn_id>`

### SKU / 이벤트 조회
- "최근 SKU 검색 10개"
  - `makestar-admin skus search --size 10`
- "SKU022138 재고/가격 상세"
  - `makestar-admin skus stock-detail SKU022138`
- "최신 이벤트 목록"
  - `makestar-admin product-events latest --display-status displayed --size 10`
- "이벤트 코드로 조회"
  - `makestar-admin product-events list-by-code --code <event_code>`
- "이벤트 상세"
  - `makestar-admin product-events detail <event_id>`
- "상품 콘텐츠 목록"
  - `makestar-admin product-contents list <product_id>`

## Reusable findings
- `/user-group/{id}` is a composite page contract, not a single API. In practice it is backed by:
  - `retrieve_user_group`
  - `list_user_group_member`
  - `list_user_group_order`
  - `deposits/balance`
  - and, once the modal opens, `deposits`
- For B2B deposit flows, distinguish the read-only pieces from write boundaries:
  - read: balance + deposit logs
  - write boundary: deposit-log note PATCH exists, but the current detail dialog is row-backed from the logs list rather than a separate read-detail endpoint
- For B2B member/group searches:
  - `search` is broad simple search
  - `company_name` behaves like partial text
  - `name_or_email` is high-precision
  - `manager_name` currently behaves closer to exact/high-precision than broad substring partial
  - `user_group_grade` works with repeated query keys, not bracket-style array encoding

## Notes
- The live SKU detail response can expose at least two price-like fields:
  - `purchasePrice` = 매입가 / cost-side price
  - `price` = general price field exposed by SKU detail
- If the current `skus_stock_detail` script summary does not print both values, inspect the raw response or query the endpoint directly with the current browser-derived token.
- When the shell token is missing, load `makestar-admin-auth-token` and stage env vars with the Bash/Git Bash or PowerShell command from that skill; use browser XHR/fetch extraction only as fallback.

## References
- `references/scripts.md`
- `references/question-patterns.md`
