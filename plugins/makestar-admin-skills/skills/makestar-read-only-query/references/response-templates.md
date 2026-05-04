# Response templates for Makestar read-only queries

Use these as operator-style answer templates after running the verified scripts.

## 1) B2B 업체 조회

### Trigger
- `대표 이메일로 업체 찾아줘`
- `업체명으로 B2B 업체 찾아줘`
- `등급 A 또는 E 업체만 보여줘`

### Recommended output
조회 기준
- 대표 이메일: jinroh78@gmail.com

결과
- 총 1건
- 주식회사 다이브원엔터테인먼트 / 상태 정상 / 등급 0(E) / 담당자 이재원 / admin jinroh78@gmail.com / 국가 KR

관련 키
- group_id: 484
- has_offline_shop: false

메모
- 더 파야 하면 바로 `user_group_detail 484 --include-balance`로 이어가면 된다.

### Notes
- list 응답에서는 업체명, 상태, 등급, 담당자, 이메일, 국가 같은 visible fields를 먼저 둔다.
- 가능하면 grade는 raw 값만 쓰지 말고 label까지 같이 적는다. 예: `0(E)`.
- `group_id`는 다음 detail drill-down에 필요하므로 trailing block에 두는 게 좋다.

## 2) 주문 조회

### Trigger
- `B2B 주문만 보여줘`
- `수령인 이름이 이다한인 주문 보여줘`
- `이벤트 코드 P_10103_BBGIRLS_3 주문만 보여줘`

### Recommended output
조회 기준
- 이벤트 코드: P_10103_BBGIRLS_3

결과
- 총 35건 (server-side total이 있으면 그 값을 우선 사용)
- server-side total이 노출되지 않는 현재 요약 스크립트라면 `현재 응답 10건`처럼 page row count라고 명시한다.
- 1) 주문번호 E-AFWQYA5 / 결제상태 CONFIRMED / 주문자 PM04 / 수령인 PM04 / 배송상태 0
- 2) 주문번호 ...
- 3) 주문번호 ...

관련 키
- order_no: C260418201844345M1
- user_code: B-AGVWSE
- user_group_id: 484

메모
- 상세가 필요하면 `orders_detail <order_no>`로 내려가면 된다.
- B2B 주문은 `--b2b`가 browser-observed tab variant를 탄다.

### Notes
- list는 top 3~10개만 compact하게 보여주는 편이 낫다.
- `paymentStatus`, `recipientName`, `shippingStatus` 같은 visible fields를 우선한다.
- `총 N건`이라고 쓸 때는 global total인지 current page row count인지 구분해서 적는다.

### 주문 상세 Notes
- `makestar-admin orders detail <order_no>` 결과를 요약할 때는 header/payment만 쓰고 끝내지 말고 ordered item row도 포함한다.
- ordered item마다 최소 `eventCode`, `productTitle`, `optionName`, `orderQuantity`를 표시한다. 이 필드들은 event/SKU contract regression anchor로 쓰인다.
- PII가 포함될 수 있으므로 이름/email/phone/address는 사용자가 명시적으로 요구하지 않으면 `[REDACTED]` 또는 최소화해서 요약한다.

## 3) 발주 조회

### Trigger
- `최근 발주 10개 보여줘`
- `PO 코드로 발주 찾아줘`
- `vendorId 126 발주 보여줘`

### Recommended output
조회 기준
- vendorId: 126

결과
- 총 N건
- 1) PO 코드 ... / 제목 ... / 벤더 ... / 생성일 ...
- 2) PO 코드 ... / 제목 ... / 벤더 ... / 생성일 ...

관련 키
- purchase_order_code: ...
- vendor_id: 126

메모
- 상세는 `purchase_orders_detail <purchase_order_code>`로 이어간다.
- ASN 연결 확인은 `advance_ship_notice_search --purchase-order-code <purchase_order_code>`로 바로 이어갈 수 있다.

### Notes
- list 요약에서는 PO 코드, 제목, 벤더, 날짜를 먼저 보여준다.
- 상세 drill-down에 필요한 `purchase_order_code`는 trailing block에 남긴다.

## 4) 빈 결과 예시

### Recommended output
조회 기준
- 업체 484 예치금 로그 / logType=DEDUCT / date=2026-04-01..2026-04-18

결과
- 총 0건
- 조건에 맞는 예치금 로그는 없었다.

메모
- empty result는 정상 read 결과다.
- 범위를 넓히려면 logType 또는 date range를 조정하면 된다.

## 5) Composite page detail 예시

### Trigger
- `업체 484 상세 보여줘`

### Recommended output
조회 기준
- group_id: 484

결과
- 업체명: 주식회사 다이브원엔터테인먼트
- 상태: 정상
- 등급: 0(E)
- 담당자: 이재원
- 관리자 이메일: jinroh78@gmail.com
- 국가: KR
- 예치금 잔액: 0.00

관련 키
- group_id: 484
- admin_user_id: 2265220
- admin_user_code: B-AGVWSE

메모
- 이 화면은 single API가 아니라 composite page다.
- 현재 기준 detail / balance / members / orders / deposit logs를 분리해서 읽는다.
