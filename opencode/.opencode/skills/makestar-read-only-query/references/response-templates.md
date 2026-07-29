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
- 1) No 603813 / 주문 번호 E-AFWQYA5 / 주문 상태 결제완료 / 주문일시 ... / 결제 번호 ... / 결제 상태 결제성공 / 결제 수단 ... / 결제금액 ... / 상품 총액 ... / 배송비 ... / 주문자명 ... / 이메일 ... / 휴대전화 번호 ... / 수취인명 ... / 수취인 이메일 ... / 수취인 휴대전화 번호 ... / 수취인 국가 ... / 우편번호 ... / 주/도시 ... / 시 ... / 주소 1 ... / 주소 2 ... / 상품/이벤트 ID ... / 이벤트 종류 ... / 이벤트 코드 ... / 발매일 ... / 상품/프로젝트명 ... / 옵션 명 ... / 주문 수량 ... / 취소 수량 ... / 배송 상태 ... / 송장 번호 ... / 택배사 ... / 출고일시 ... / 배송요청 사항 ... / 관리자 배송요청 사항 ... / 배송준비일시 ... / 재고 할당일시 ... / 재고할당 ...
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
- list는 top 3~10개를 보여주되, 각 row에는 admin 화면에 보이는 screen-visible field를 빠뜨리지 않는다.
- `paymentStatus`, `recipientName`, `shippingStatus` 같은 visible fields를 우선한다.
- `총 N건`이라고 쓸 때는 global total인지 current page row count인지 구분해서 적는다.

### 주문 상세 Notes
- `makestar-admin orders detail <order_no>` 결과를 요약할 때는 header/payment만 쓰고 끝내지 말고 화면의 상품정보/배송정보 row도 포함한다.
- ordered item마다 화면 기준 `productEventId`, `eventType`, `productEventCode`, `releasedAt`, `productEventName`, `productEventOptionName`, `orderQuantity`, `cancelQuantity`를 표시한다. 이 필드들은 event/SKU contract regression anchor로 쓰인다.
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

## 5) 안전재고 이하 SKU 조회

### Trigger
- `안전재고 이하 SKU만 보여줘`
- `안전재고 위험 SKU 전체 목록 보여줘`

### Recommended output
조회 기준
- 안전재고 이하 SKU: `--below-safety-quantity-only Y`

결과
- 총 46건
- 1) SKU017304 / 베이비몬스터(BABYMONSTER)|WEGOUP|POSTCARDVer. / 가용재고 0 / 안전재고 108 / 박스당 수량 54
- 2) SKU014747 / XLOV(XLOV)|IONE|1(ONE)VER. / 가용재고 58 / 안전재고 88 / 박스당 수량 88
- 3) SKU014217 / P1Harmony(P1Harmony)|DUH!|CompactVer. / 가용재고 0 / 안전재고 120 / 박스당 수량 1

관련 키
- sku_code: SKU017304
- production_company_product_code: YGP0672
- distribution_code: 8800320199413

메모
- `safetyQuantity`가 안전재고이고, `vendorPackSize`는 박스당 수량이다.
- 안전재고 위험 여부는 `availableQuantity <= safetyQuantity` 관계로 판단된다.
- `vendorPackSize`와 `safetyQuantity`가 우연히 같은 SKU도 있으므로 둘을 같은 값으로 추정하지 않는다.

### Notes
- SKU list 응답에서는 `skuCode`, `skuName`, `availableQuantity`, `safetyQuantity`, `vendorPackSize`를 먼저 둔다.
- 전체 목록을 요청받으면 서버 total(`resData.totCnt`)을 우선 사용하고, 필요하면 `--size`를 total 이상으로 키워 한 번에 가져온다.

## 6) Composite page detail 예시

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

## 7) 대분류(product) 조회

### Trigger
- `최근 대분류 10개 보여줘`
- `상품코드로 대분류 찾아줘`
- `이번 달 발매되는 대분류 보여줘`

### Recommended output
조회 기준
- 발매일: 2026-08-01..2026-08-31

결과
- 전체 4,319건 / 현재 페이지 10건
- 1) ID 10949 / 앨범코드 M01267530743566900 / 이름 ... / 아티스트 ... / 공급사/제작사 ... / 발매일 ... / 담당자 ...
- 2) ID 10948 / 앨범코드 ... / 이름 ... / 아티스트 ... / 공급사/제작사 ... / 발매일 ... / 담당자 ...

관련 키
- product_id: 10949
- artist_id: ...
- company_id: ...
- manager_id: ...
- created_at: ...

메모
- 대분류는 `product`, 상품은 `product_event`다.
- 전체 건수는 `pagination.count`, 현재 페이지 건수는 `product_list` 길이다.
- `created_at`/`released_at` 기간 조회에는 시작일과 종료일을 모두 전달한다.

### Notes
- 화면 visible fields인 ID, 앨범코드(전체), 이름, 아티스트, 공급사/제작사, 발매일, 담당자를 먼저 보여준다.
- `createdAt`은 기간 조회와 후속 연결에 유용하지만 현재 목록의 visible column은 아니므로 related key로 둔다.
- 응답의 `pagination.next`가 direct API host를 가리켜도 그 URL을 직접 따라가지 말고 CLI의 `--page`를 사용한다.
