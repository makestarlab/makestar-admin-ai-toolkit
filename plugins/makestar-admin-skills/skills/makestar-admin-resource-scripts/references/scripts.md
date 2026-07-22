Usage pattern notes:
- Start from the question pattern examples in `SKILL.md` or `references/question-patterns.md`.
- As of the 2026-04-18 CLI help audit, the documented examples for grade filtering, order event-code filtering, and B2B order filtering are aligned to actual script flags.
- Stay read-only: query scripts are allowed; create/update/delete are not.
- If a requested filter is not exposed by the current script CLI, inspect the script help or resource contract before inventing flags.
- For `skus search`, `safetyQuantity` is 안전재고 and `vendorPackSize` is 박스당 수량; keep both visible and separate in operator summaries.
- For `skus stock-detail`, distributor deadline fields are detail-only: `distributorPreOrderDeadline` is 유통사 선주문 발주 마감일 and `distributorFinalOrderDeadline` is 유통사 최종 발주 마감일.
- For B2B `/user-group/{id}` questions, remember the page is composite: detail, members, orders, deposit balance, and deposit logs are separate reads.
- For deposit log detail questions, use the logs list row as the read model; do not assume a separate detail GET exists.

Reference lookup commands:
- `makestar-admin reference-lookups artists --search <artist_name> --limit 10`
  - Admin artist list; searches every localized name and renders Korean-compatible `artistName` plus `artistNameEn`, `artistNameJa`, and `artistNameZh`. The selected id is used as SKU `artistId` or 대분류 `artist_id` according to the target form.
- `makestar-admin reference-lookups manufacturers --search <company_name> --limit 10`
  - Admin V2 company list constrained to `role=MANUFACTURER`; each company is one row with Korean-compatible `companyName` plus `companyNameEn`, `companyNameJa`, and `companyNameZh`. SKU 유통사 maps to `productionCompanyId`.
- `makestar-admin reference-lookups orderers --search <company_name> --limit 10`
  - Admin V2 company list constrained to `role=ORDERER`; each company is one row with Korean-compatible `companyName` plus `companyNameEn`, `companyNameJa`, and `companyNameZh`. SKU 발주처 maps to `vendorId`.
- `makestar-admin reference-lookups sku-categories --search <category_name_or_code> --limit 10`
  - OMS SKU type/category metadata and dimensional/customs defaults; not 대분류(product) or a display category.
- `--search` and `--limit` filter the rendered summary locally after the GET response. Artist/company search includes every multilingual name-map value. `--raw` returns the full unfiltered API response including `i18n_name`/`i18nName`.
