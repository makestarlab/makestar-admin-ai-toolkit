# Verified routes for Makestar read-only queries

These commands were chosen to match the actual current script CLI surface.

## B2B 업체 / 담당자
- 대표 이메일로 업체 찾기
  - question: `대표 이메일 jinroh78@gmail.com 으로 B2B 업체 찾아줘`
  - command: `makestar-admin user-groups list --name-or-email <email> --size 10`
- 업체명으로 업체 찾기
  - question: `업체명 다이브원으로 B2B 업체 찾아줘`
  - command: `makestar-admin user-groups list --company-name <company> --size 10`
- 담당자 이름으로 업체 찾기
  - question: `담당자 이재원인 B2B 업체 찾아줘`
  - command: `makestar-admin user-groups list --manager-name <manager> --size 10`
- 국가 코드로 업체 좁히기
  - question: `KR 업체만 보여줘`
  - command: `makestar-admin user-groups list --country-code KR --size 10`
- 오프라인 매장 있는 업체만
  - question: `오프라인 매장 있는 B2B 업체만 보여줘`
  - command: `makestar-admin user-groups list --has-offline-store True --size 10`
- 등급 A 또는 E 업체만
  - question: `등급 A 또는 E 업체만 보여줘`
  - command: `makestar-admin user-groups list --user-group-grade 4 --user-group-grade 0 --size 10`

## B2B 업체 상세 / 활동
- 업체 상세 + 잔액
  - question: `업체 484 상세 보여줘`
  - command: `makestar-admin user-groups detail <group_id> --include-balance`
- 업체 멤버 목록
  - question: `업체 484 멤버 목록 보여줘`
  - command: `makestar-admin user-groups members list <group_id>`
- 업체 주문 활동
  - question: `업체 478 주문 활동 보여줘`
  - command: `makestar-admin user-groups orders list <group_id>`
- 업체 예치금 로그
  - question: `업체 477 예치금 로그 보여줘`
  - command: `makestar-admin user-groups deposit-logs list <group_id>`
- 업체 예치금 EARN만
  - question: `업체 477 예치금 EARN만 보여줘`
  - command: `makestar-admin user-groups deposit-logs list <group_id> --log-type EARN`
- 업체 예치금 로그 날짜 범위
  - question: `업체 477 예치금 로그를 2026-03-31 하루만 보여줘`
  - command: `makestar-admin user-groups deposit-logs list <group_id> --start-date 2026-03-31 --end-date 2026-03-31`

## Orders
- 최근 주문
  - question: `최근 주문 10개 보여줘`
  - command: `makestar-admin orders list --size 10`
- 이벤트 코드 기준 주문
  - question: `이벤트 코드 P_10103_BBGIRLS_3 주문만 보여줘`
  - command: `makestar-admin orders list --product-event-code <event_code> --size 10`
- B2B 주문
  - question: `B2B 주문만 보여줘`
  - command: `makestar-admin orders list --b2b --size 10`
- 수령인 이름 기준 주문
  - question: `수령인 이름이 이다한인 주문 보여줘`
  - command: `makestar-admin orders list --recipient-name <name> --size 10`
- 배송 상태 기준 주문
  - question: `배송상태 0인 주문 보여줘`
  - command: `makestar-admin orders list --shipping-status 0 --size 10`
- 주문 상세
  - question: `주문번호 C260418201844345M1 상세 보여줘`
  - command: `makestar-admin orders detail <order_no>`

## Purchase / inbound / ASN
- 최근 발주
  - question: `최근 발주 10개 보여줘`
  - command: `makestar-admin purchase-orders list --size 10`
- 발주 코드로 찾기
  - question: `PO 코드로 발주 찾아줘`
  - command: `makestar-admin purchase-orders list --purchase-order-code <po_code> --size 10`
- 벤더 기준 발주
  - question: `vendorId 126 발주 보여줘`
  - command: `makestar-admin purchase-orders list --vendor-id <vendor_id> --size 10`
- 발주 상세
  - question: `발주서 PO 코드 상세 보여줘`
  - command: `makestar-admin purchase-orders detail <purchase_order_code>`
- 구매요청 목록
  - question: `구매요청 목록 보여줘`
  - command: `makestar-admin purchase-requests list --size 10`
- 상태 기준 구매요청
  - question: `REQUESTED 상태 구매요청 보여줘`
  - command: `makestar-admin purchase-requests list --status REQUESTED --size 10`
- 구매요청 상세
  - question: `구매요청 상세 보여줘`
  - command: `makestar-admin purchase-requests detail <purchase_order_request_id>`
- 발주 연결 ASN
  - question: `PO 코드에 연결된 ASN 찾아줘`
  - command: `makestar-admin advance-ship-notices search --purchase-order-code <purchase_order_code>`
- 입고 상세
  - question: `입고 상세 보여줘`
  - command: `makestar-admin inbounds detail --purchase-order-code <po_code> --goods-received-note-id <grn_id>`

## SKU / event
- 최근 SKU
  - question: `최근 SKU 10개 보여줘`
  - command: `makestar-admin skus search --size 10`
- 안전재고 이하 SKU
  - question: `안전재고 이하 SKU만 보여줘`
  - command: `makestar-admin skus search --below-safety-quantity-only Y --size 10`
- 벤더 기준 SKU
  - question: `vendorId 126 SKU 보여줘`
  - command: `makestar-admin skus search --vendor-id <vendor_id> --size 10`
- SKU 재고/가격 상세
  - question: `SKU022138 재고와 가격 상세 보여줘`
  - command: `makestar-admin skus stock-detail <sku_code>`
- 최신 이벤트 목록
  - question: `최신 이벤트 목록 보여줘`
  - command: `makestar-admin product-events latest --display-status displayed --size 10`
- 판매 종료일 기준 상품/이벤트 검색
  - question: `2026-05-17에 판매 종료되는 상품 보여줘`
  - command: `makestar-admin product-events latest --period-type sales_end_at --end-date 2026-05-17 --size 10`
  - note: `period_type` is an API contract value. Use `sales_end_at`; do not use the UI/model camelCase key `salesEnd`.
- 이벤트 코드 조회
  - question: `이벤트 코드로 조회해줘`
  - command: `makestar-admin product-events list-by-code --code <event_code>`
- 이벤트 상세
  - question: `이벤트 상세 보여줘`
  - command: `makestar-admin product-events detail <event_id>`
- 상품 콘텐츠 목록
  - question: `상품 콘텐츠 목록 보여줘`
  - command: `makestar-admin product-contents list <product_id>`

## Recommended response format
- Lists
  - start with the filter the user asked for
  - then show total count
  - then show top rows compactly using visible fields first
  - include ids/keys only when they help the next lookup
- Details
  - start with the main visible fields the operator cares about
  - then add related ids/keys in a short secondary block
  - mention composite-page structure when relevant
- Empty results
  - report them as a normal read result
  - do not frame empty data as an error unless the API actually failed

Suggested compact output pattern:
1. what was queried
2. count or hit status
3. visible fields
4. related ids/keys
5. important contract nuance if needed

## Boundaries
- Read-only only.
- If a filter is not exposed here, inspect the broader contract skill before adding new command examples.
- Do not turn documented write boundaries into executable commands here.
