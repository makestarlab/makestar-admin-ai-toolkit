# 포토카드 SKU OPP read-only API scripts

Use this reference when a Makestar admin task mentions `포토카드 SKU OPP 작업`, especially the two UI tabs `요청 관리` and `입고~작업 관리`.

## Durable contract shape

- Treat the page as a read-only resource family, not a write flow.
- The page has at least two visible top-level tabs:
  - `요청 관리`
  - `입고~작업 관리`
- Keep the resource scripts separate by API family:
  - `photocard-skus list`: SKU OPP request/inspection list rows.
  - `photocard-skus statistics`: status badge/counter summary for the OPP SKU workflow.
  - `photocard-work-requests list`: OPP work-request rows by work status.
  - `photocard-sku-opp-work verify`: page-level composite verifier for the full screen contract.

## Standard commands

- Request-management default list:
  - `makestar-admin photocard-skus list --size 10`
- Inspection/status slices for `입고~작업 관리`:
  - `makestar-admin photocard-skus list --inspection-status PENDING --size 10`
  - `makestar-admin photocard-skus list --inspection-status INSPECTING --size 10`
  - `makestar-admin photocard-skus list --inspection-status PARTIALLY_COMPLETED --size 10`
  - `makestar-admin photocard-skus list --inspection-status COMPLETED --size 10`
- Status badge/counter summary:
  - `makestar-admin photocard-skus statistics --json`
- Work-request status slices:
  - `makestar-admin photocard-work-requests list --work-request-status WAITING --size 10`
  - `makestar-admin photocard-work-requests list --work-request-status IN_PROGRESS --size 10`
  - `makestar-admin photocard-work-requests list --work-request-status COMPLETED --size 10`
- Page-level composite verification:
  - `makestar-admin photocard-sku-opp-work verify --size 1 --json`

## Page-level verifier semantics

`makestar-admin photocard-sku-opp-work verify` performs these read-only probes:

1. `요청 관리` default SKU list.
2. `입고~작업 관리` statistics counters.
3. `입고 전` SKU list.
4. `검수 중` SKU list.
5. `부분 입고 완료` SKU list.
6. `입고 완료` SKU list.
7. `작업 대기` work-request list.
8. `작업 중` work-request list.
9. `작업 완료` work-request list.

Use this command when the user asks whether the whole screen contract still works. Use the individual list/statistics commands when they ask about one tab/status/resource.

## Regression harness pattern

When adding or changing these scripts:

1. Add/update resource YAML under `resources/photocard-skus/` or `resources/photocard-work-requests/`.
2. Add/update source scripts under `scripts/resources/` or the page-level helper under `scripts/helpers/`.
3. Expose CLI handlers in `scripts/cli/registry.py` and console scripts in `pyproject.toml`.
4. Add HTML help entries; full test discovery asserts every registry handler appears in rendered HTML.
5. Add semantic rows to `scripts/verify_admin_api_regression.py`.
6. Update `docs/admin-api-live-regression.md` totals and `docs/resource-semantics-matrix.md`.
7. Rebuild the packaged CLI through the project release/build workflow and verify the installed command path if helper modules were added:
   - `makestar-admin photocard-sku-opp-work verify --help`
8. Verify with the project-owned test and live-regression commands from the repository checklist. At minimum cover:
   - Python compile checks for touched modules.
   - CLI help/registry/build-spec unit tests.
   - Full unit discovery.
   - `scripts/verify_admin_api_regression.py --output artifacts/admin-api-live-regression-photocard-opp.json`

## Pitfalls

- Do not stop after adding CLI registry handlers; `tests/test_cli_html_help.py` requires matching `scripts/cli/html_help.py` command docs for every handler.
- Do not stop after source CLI works; new helper modules must be included in `scripts/build/makestar-admin.spec` hidden imports or the PyInstaller binary can return `unknown command`.
- Zero rows for a status slice can still be a valid API shape if the command exits 0 and semantic assertions accept the empty state intentionally.
- The `productCode` filter on work requests has backend event/product-code semantics, not necessarily the visible product cell. Prefer `--main-product-code` when that is what the UI/source semantics require.
- In final reports, call out unrelated dirty worktree paths separately so JG can distinguish this task's changes from existing operator docs or other work.
