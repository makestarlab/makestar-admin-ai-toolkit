# Korean Question Patterns -> Internal Commands -> Expected Output

Use this as a fast routing sheet for read-only Makestar admin queries.

## B2B 업체 찾기

### 대표 이메일로 업체 찾기
- Question:
  - `대표 이메일 jinroh78@gmail.com 으로 B2B 업체 찾아줘`
- Command:
  - `makestar-admin user-groups list --name-or-email jinroh78@gmail.com --size 10`
- Expected output:
  - matching group rows
  - `id`, `name`, `admin_name`, `admin_user_email`, `country_code`, `has_offline_shop`, `grade`, `is_active`

### 업체명으로 찾기
- Question:
  - `업체명 다이브원으로 B2B 업체 찾아줘`
- Command:
  - `makestar-admin user-groups list --company-name 다이브원 --size 10`
- Expected output:
  - matching company-oriented rows
  - if multiple hits, narrow further with manager or country

### 담당자 이름으로 찾기
- Question:
  - `담당자 이재원인 B2B 업체 찾아줘`
- Command:
  - `makestar-admin user-groups list --manager-name 이재원 --size 10`
- Expected output:
  - high-precision manager-name matches
  - do not assume broad substring semantics

### 등급 A 또는 E 업체만
- Question:
  - `등급 A 또는 E 업체만 보여줘`
- Command:
  - `makestar-admin user-groups list --user-group-grade 4 --user-group-grade 0 --size 10`
- Expected output:
  - rows matching repeated `user_group_grade` query keys
  - this is a verified CLI mapping for the repeated-key wire contract

## B2B 업체 상세 / 활동

### 업체 상세
- Question:
  - `업체 484 상세 보여줘`
- Command:
  - `makestar-admin user-groups detail 484 --include-balance`
- Expected output:
  - group primary object
  - balance summary
  - admin identity and discount-related fields visible from the detail payload

### 업체 멤버 목록
- Question:
  - `업체 484 멤버 목록 보여줘`
- Command:
  - `makestar-admin user-groups members list 484`
- Expected output:
  - paginated member rows
  - manager badge semantics from `role`
  - B2B/B2C site semantics from `user.has_group`

### 업체 주문 활동
- Question:
  - `업체 478 주문 활동 보여줘`
- Command:
  - `makestar-admin user-groups orders list 478`
- Expected output:
  - group-scoped order list
  - `orderNumber`, `userOrderNumber`, `paymentStatus` and other visible activity fields

### 업체 예치금 로그
- Question:
  - `업체 477 예치금 로그 보여줘`
- Command:
  - `makestar-admin user-groups deposit-logs list 477`
- Expected output:
  - paginated deposit logs
  - `depositLogId`, `logType`, `amount`, `afterAmount`, `currency`, `createdAt`

### 업체 예치금 로그를 타입으로 좁히기
- Question:
  - `업체 477 예치금 EARN만 보여줘`
- Command:
  - `makestar-admin user-groups deposit-logs list 477 --log-type EARN`
- Expected output:
  - only EARN rows
  - empty result is still valid output

### 업체 예치금 로그를 날짜로 좁히기
- Question:
  - `업체 477 예치금 로그를 2026-03-31 하루만 보여줘`
- Command:
  - `makestar-admin user-groups deposit-logs list 477 --start-date 2026-03-31 --end-date 2026-03-31`
- Expected output:
  - logs within the confirmed date window
  - preserve raw string amount fields

## 주문 조회

### 최근 주문
- Question:
  - `최근 주문 10개 보여줘`
- Command:
  - `makestar-admin orders list --size 10`
- Expected output:
  - latest visible orders under the script default query contract

### 특정 주문 상세
- Question:
  - `주문번호 C260418201844345M1 상세 보여줘`
- Command:
  - `makestar-admin orders detail C260418201844345M1`
- Expected output:
  - order detail summary
  - note whether it came from OMS-first path or admin fallback behavior if the script exposes that nuance

### 특정 이벤트 코드 주문만
- Question:
  - `이벤트 코드 P_10103_BBGIRLS_3 주문만 보여줘`
- Command:
  - `makestar-admin orders list --product-event-code P_10103_BBGIRLS_3 --size 10`
- Expected output:
  - orders narrowed by `product_event_code`

### B2B 주문만
- Question:
  - `B2B 주문만 보여줘`
- Command:
  - `makestar-admin orders list --b2b --size 10`
- Expected output:
  - browser-observed B2B tab variant
  - `customer_type=b2b` path applied by the script

## 구매 / 발주 / 입고 / ASN

### 최근 발주
- Question:
  - `최근 발주 10개 보여줘`
- Command:
  - `makestar-admin purchase-orders list --size 10`
- Expected output:
  - latest purchase order rows

### 발주 상세
- Question:
  - `발주서 PO 코드 상세 보여줘`
- Command:
  - `makestar-admin purchase-orders detail <purchase_order_code>`
- Expected output:
  - full purchase order detail summary with visible fields and related ids

### 구매요청 목록
- Question:
  - `구매요청 목록 보여줘`
- Command:
  - `makestar-admin purchase-requests list --size 10`
- Expected output:
  - latest purchase request rows

### 구매요청 상세
- Question:
  - `구매요청 상세 보여줘`
- Command:
  - `makestar-admin purchase-requests detail <purchase_order_request_id>`
- Expected output:
  - request detail with visible fields and related ids

### 특정 PO의 ASN 찾기
- Question:
  - `PO 코드에 연결된 ASN 찾아줘`
- Command:
  - `makestar-admin advance-ship-notices search --purchase-order-code <purchase_order_code>`
- Expected output:
  - ASN search results tied to the purchase order

### 입고 상세
- Question:
  - `입고 상세 보여줘`
- Command:
  - `makestar-admin inbounds detail --purchase-order-code <po_code> --goods-received-note-id <grn_id>`
- Expected output:
  - inbound detail visible on the integrated-admin screen

## SKU / 이벤트 조회

### SKU 검색
- Question:
  - `최근 SKU 10개 보여줘`
- Command:
  - `makestar-admin skus search --size 10`
- Expected output:
  - SKU search rows under the default search body

### SKU 재고/가격 상세
- Question:
  - `SKU022138 재고와 가격 상세 보여줘`
- Command:
  - `makestar-admin skus stock-detail SKU022138`
- Expected output:
  - stock detail summary
  - include both `price` and `purchasePrice` when present

### 최신 이벤트 목록
- Question:
  - `최신 이벤트 목록 보여줘`
- Command:
  - `makestar-admin product-events latest --display-status displayed --size 10`
- Expected output:
  - latest displayed event rows

### 이벤트 코드 조회
- Question:
  - `이벤트 코드로 조회해줘`
- Command:
  - `makestar-admin product-events list-by-code --code <event_code>`
- Expected output:
  - event rows matching the code

### 상품 콘텐츠 목록
- Question:
  - `상품 콘텐츠 목록 보여줘`
- Command:
  - `makestar-admin product-contents list <product_id>`
- Expected output:
  - product content rows for the target product

## Safety / Boundary Notes
- Read-only only.
- Do not execute create/update/delete endpoints from these question patterns.
- If the user asks for a filter not exposed by the script CLI, inspect the script help or the resource contract before inventing CLI flags.
- `/user-group/{id}` questions are usually composite. Split into detail, members, orders, deposit balance, and deposit logs as needed.
- Deposit log detail currently reuses the logs-list row as its read model; do not assume a separate detail GET exists.
