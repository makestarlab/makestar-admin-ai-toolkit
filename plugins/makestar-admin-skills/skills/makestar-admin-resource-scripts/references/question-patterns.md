# Korean Question Patterns -> Internal Commands -> Expected Output

Use this as a fast routing sheet for read-only Makestar admin queries.

## 등록 기준정보 조회

### 아티스트 후보
- Question:
  - `아티스트 PLAVE 찾아줘`
- Command:
  - `makestar-admin reference-lookups artists --search PLAVE --limit 10`
- Expected output:
  - matching artist ids and Korean, English, Japanese, and Chinese names from the Admin artist list
  - search can match any value in `i18n_name`

### SKU 유통사 후보
- Question:
  - `SKU 유통사 후보 찾아줘`
- Command:
  - `makestar-admin reference-lookups manufacturers --search <company_name> --limit 10`
- Expected output:
  - one company row per `role=MANUFACTURER` result, with Korean, English, Japanese, and Chinese names from V2 `i18nName`
  - selected `companyId` maps to SKU `productionCompanyId`

### SKU 발주처 후보
- Question:
  - `SKU 발주처 후보 찾아줘`
- Command:
  - `makestar-admin reference-lookups orderers --search <company_name> --limit 10`
- Expected output:
  - one company row per `role=ORDERER` result, with Korean, English, Japanese, and Chinese names from V2 `i18nName`
  - selected `companyId` maps to SKU `vendorId`

### SKU 카테고리와 기본 사양
- Question:
  - `앨범 SKU 카테고리와 기본 규격 찾아줘`
- Command:
  - `makestar-admin reference-lookups sku-categories --search <category_name_or_code> --limit 10`
- Expected output:
  - OMS SKU type/category code and name
  - dimensional, volume, HS-code, and customs-description defaults when present
  - this is not 대분류(product) or a B2C/B2B display category

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

### 재고할당/배송준비전 주문
- Question:
  - `결제완료 상품 중 배송준비전이라 재고할당 필요한 주문 보여줘`
  - `재고할당 필요한 주문을 엑셀에서 볼 수 있게 저장해줘`
- Command:
  - `makestar-admin orders list --stock-allocation-needed --size 10`
  - `makestar-admin orders list --stock-allocation-needed --size 100 --csv-out stock-allocation-needed-orders.csv`
- Expected output:
  - 결제완료 + 상품 + 배송준비전 주문 rows
  - preset query fields: `order_status=2`, `product_event_type=product`, `payment_status=CONFIRMED`, `delivery_requested=false`
  - CSV output is read-only archival/export support; 배송준비완료 상태 변경 is still an integrated-admin operator action

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
  - include `availableQuantity`, `safetyQuantity`, and `vendorPackSize` when present

### 안전재고 이하 SKU 검색
- Question:
  - `안전재고 이하 SKU만 보여줘`
  - `안전재고 위험 SKU 전체 목록 보여줘`
- Command:
  - `makestar-admin skus search --below-safety-quantity-only Y --size 10`
- Expected output:
  - SKU rows whose 가용재고 is at or below 안전재고
  - `availableQuantity` = 가용재고
  - `safetyQuantity` = 안전재고
  - `vendorPackSize` = 박스당 수량

### SKU 재고/가격 상세
- Question:
  - `SKU022138 재고와 가격 상세 보여줘`
- Command:
  - `makestar-admin skus stock-detail SKU022138`
- Expected output:
  - stock detail summary
  - include both `price` and `purchasePrice` when present
  - include `distributorPreOrderDeadline` (유통사 선주문 발주 마감일) and `distributorFinalOrderDeadline` (유통사 최종 발주 마감일) when present; these are not list/search fields in current live evidence

### 최신 이벤트 목록
- Question:
  - `최신 이벤트 목록 보여줘`
- Command:
  - `makestar-admin product-events latest --display-status displayed --size 10`
- Expected output:
  - latest displayed event rows

### 판매 종료일 기준 상품/이벤트 검색
- Question:
  - `2026-05-17에 판매 종료되는 상품 보여줘`
- Command:
  - `makestar-admin product-events latest --period-type sales_end_at --end-date 2026-05-17 --size 10`
- Expected output:
  - product/event rows whose selected period filter matches the requested KST date
  - use `sales_end_at`, not the API-invalid camelCase value `salesEnd`

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
