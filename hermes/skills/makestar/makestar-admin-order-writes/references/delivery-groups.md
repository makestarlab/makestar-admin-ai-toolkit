# Delivery-group CLI contract

Required CLI: `makestar-admin >=0.3.0`. Source-confirmed on 2026-10-15; offline tests and mocked API checks do not prove deployment or live Stage execution.

## Read the current work unit

```bash
makestar-admin delivery-groups list --commerce-order-no ORDER --json
makestar-admin delivery-groups list --delivery-group-no DG-ORDER-01 --delivery-group-no DG-ORDER-02 --json
makestar-admin delivery-groups list --commerce-order-no ORDER --include-amounts --json
makestar-admin delivery-groups detail DG-ORDER-01 --json
makestar-admin delivery-groups history DG-ORDER-01 --json
makestar-admin delivery-groups allocations DG-ORDER-01 --include-released --json
makestar-admin delivery-groups snapshot ORDER --json
makestar-admin delivery-groups status ORDER --json
makestar-admin releases list --delivery-group-no DG-ORDER-01 --include-cancelled --include-events --json
makestar-admin releases detail REL-1 --json
makestar-admin delivery-parcels list --delivery-group-no DG-ORDER-01 --json
makestar-admin delivery-parcels detail PAR-1 --json
makestar-admin delivery-groups cancellation-options ORDER --json
```

Reads default to production. Add `--env stage` for Stage. Example identifiers are placeholders, not usable fixtures. Lists require an order/group identifier. Release/Parcel lists also accept their own identifiers, have zero-based `--page`, and `--size` 1–100; they return one page and its `totalElements`, not an automatically collected full ledger. Group list limits repeated selectors to 100 and uses repeated query keys, not `key[]` or comma-separated values. `--include-amounts` requires exactly one order and no group/status/superseded filter. Unavailable amounts remain unavailable, not zero.

`orders list --include-delivery-details --size 100 --json` requests the current `delivery_details` alongside the existing order list. Its pagination is still by order. `deliveryGroupManaged` in the default order summary uses the top-level managed predicate, with the old nested location as fallback. Use group commands for group instructions and execution state.

## Interpret state without collapsing it

`status ORDER` reads one authoritative fulfillment snapshot and checks order/revision consistency across groups, Releases and Parcels. `--json` emits the derived per-group state; `--raw` emits the underlying snapshot. Source-provided `allowedActions` and `actionBlockedReasons` are retained in JSON and do not grant authorization to execute.

| Output | Meaning |
|---|---|
| `reservedAllocationComplete` | All active group lines are fully RESERVED now. After consumption this may be false; it is not historical proof that allocation never happened. No lines means unknown (`null`). |
| `releaseCreated` | A non-cancelled Release exists. `CREATED` is not WMS transmission. |
| `wmsSent` | For a `WMS` route, active Release is `SENT` or `CONFIRMED`. Non-WMS routes, `SENDING`, `SEND_UNKNOWN`, `CANCEL_REQUESTED` or unknown states yield `null`. A `DIRECT` Release can be `SENT` without an external WMS call. |
| `shipmentConfirmed` | An active Release is `CONFIRMED`. |
| `deliveryComplete` | Every current Parcel is `DELIVERED`. No Parcel or an unknown/error status means unknown. |
| `releaseStates`, `parcelStates` | Original server values; preserved independently of UI labels. |

`READY` and the UI labels 설정중/확정 do not establish allocation, WMS send or delivery completion. `COMPLETED` can represent a non-WMS handover. `deliveryGroupCreationPending=true` must not be mistaken for a legacy order or a successfully created group.

## Explicit group commands

Mutation commands consume a UTF-8 JSON object through `--body-file`. This is the exact API body: camelCase, no extra envelope. Revisions come from fresh snapshot/detail reads. Each command validates the request before authentication or network I/O.

```bash
# request.json: {"deliveryGroupNos":["DG-ORDER-01"],"expectedRevision":4}
makestar-admin delivery-groups allocate --body-file request.json --json
# After authorization for these exact Stage targets:
makestar-admin delivery-groups allocate --body-file request.json --commerce-order-no ORDER --env stage --execute --confirm-stage-write --json
makestar-admin delivery-groups status ORDER --env stage --json
makestar-admin delivery-groups allocations DG-ORDER-01 --env stage --json
```

The three allocation commands require `--commerce-order-no` for execution to check the receipt owner; this flag is not added to the body. All writes default to an offline dry-run and use the fixed Stage origin even if a custom base URL is configured. Every actual write requires exactly `--env stage --execute --confirm-stage-write`. There is no production execution switch. Do not run live writes in unattended CI.

| `delivery-groups` command | JSON request body |
|---|---|
| `allocate` | `deliveryGroupNos`, `expectedRevision`; optional `expectedGroups[{sourceDeliveryGroupKey,compositionRevision}]` for initial local groups |
| `allocate-manual` | Same scope/revision plus **one of** `allocations[{deliveryGroupLineId,stockItemQuantityId,quantity}]` or `manualSelections[{sourceDeliveryGroupKey,sourceLineItemId,skuCode,quantity}]`. Initial manual selections also require `expectedGroups`. |
| `reset-allocation` | `deliveryGroupNos`, `expectedRevision` |
| `set-delivery-prepared` | `deliveryGroupNos`, `deliveryRequested` boolean |
| `set-execution-properties` | `items[{deliveryGroupNo,expectedRevision,expectedCompositionRevision?,desiredState:{fulfillmentRoute,plannedCarrierCode?,managementInstruction?}}]` |
| `cancel` | `items[{deliveryGroupNo,expectedRevision,reason}]`. Cancels fulfillment groups; this is **not payment cancellation/refund**. |
| `hold` | `deliveryGroupNos`, `expectedRevision`, `holdReason`; optional `holdMemo`, `resumeCondition` |
| `resume` | `deliveryGroupNos`, `expectedRevision` |
| `complete-non-wms` | Scope/revision, `completionType` (`EXTERNAL_SHIPPED`, `EVENT_SITE_DELIVERED`, `ONSITE_HANDED_OUT`), `operationSnapshot:{reason,evidence}` |
| `update-composition` | `commerceOrderNo`, `expectedGroups`, `groups`; preserve the optional UUID `requestId` across recovery. Each group has nullable `scheduledShipDate` and `options[{sourceLineItemId,optionId,quantity}]`; existing groups carry `sourceDeliveryGroupKey` and `compositionRevision`, new children can carry `parentSourceDeliveryGroupKey`. |
| `record-blocked-failures` | `items[{commerceOrderNo,deliveryGroupNo}]`, maximum 500. Writes failure history, not stock allocation. |
| `backfill` | Optional `userOrderNumber` (comma-separated original order numbers), `dryRun` (server default true), `limit` (default 20, max 100), `afterOrderPk`, `throughOrderPk`. This is **Commerce local-plan backfill**, not OMS migration backfill. |

Most group/Release scopes accept at most 100 items. The CLI does not silently split a request or change revisions between requests. Submit deliberately scoped batches and inspect each receipt before the next batch. Fulfillment routes are `WMS`, `DIRECT`, `EXTERNAL`, `EVENT_SITE`; changing carrier alone must not invent a route change.

### Release creation and WMS execution

```json
{"deliveryGroupNos":["DG-ORDER-01"],"idempotencyKey":"operator-request-unique-stable-key"}
```

Pass that body to `releases create`. Creation produces `REL-...` identifiers and normally `CREATED`; it does not send the WMS instruction. Inspect the returned Release ledger before `releases send`.

| `releases` command | JSON body |
|---|---|
| `create` | `deliveryGroupNos`, `idempotencyKey` (max 128) |
| `send` | `releaseNos`, optional `chunkSize` (default 10) |
| `cancel` | `releaseNos`, optional `reason` |
| `retry` | `releaseNos`, optional `chunkSize`; an explicit recovery command for eligible failed Releases, never an automatic retry |

`cancel` cancels the WMS release request; it does not cancel the commercial order or reset allocation. Confirm `CANCELLED` and group `READY` by readback; ambiguous WMS cancellation can remain `CANCEL_REQUESTED`.

Send can return an already processed `SENT`/`CONFIRMED` receipt, or `CONFIRMED` if the WMS callback won the response race. Keep the per-item code. For route `DIRECT`, `DIRECT_RELEASE_ACCEPTED` means local direct-shipping acceptance without external WMS transmission; inspect the group route and ledger.

### Read-only POSTs

These execute against `--env prod|stage` without write flags. They compute/read only, unlike an offline mutation dry-run:

- `delivery-groups manual-preview --body-file request.json`: `deliveryGroupNos`, `expectedRevision`.
- `releases preview --body-file request.json`: `deliveryGroupNos`. Inspect missing groups, conflicts, warnings and every allocation invariant before create.
- `delivery-groups cancellation-shipping-quote --body-file request.json`: `commerceOrderNo`, `expectedRevision`, `optionList[{deliveryGroupNo,eventId,optionId,quantity}]`. Amounts remain decimal strings. A quote does not save or refund; payment cancellation and `shipping_refunds` submission are not exposed by this CLI.

## Receipt and recovery rules

- Exit code zero means a structurally valid accepted receipt for the requested scope, not independently verified final state. Writes retain `verified=false`, `readbackRequired=true`, the exact request and the full response.
- Inspect item `status`, `code`, `message`, `details` and result counts. Partial failures return nonzero. Known no-change outcomes such as `ALREADY_DESIRED_STATE` are distinct from unknown skips.
- Transport errors, malformed receipts, identity/revision mismatches and unknown statuses require ledger readback. The CLI never automatically retries or changes the supplied idempotency key.
- Compare the selected group and its siblings before/after. Read group allocations, Release details and the order snapshot. Re-read history when investigating a partial result; `complete=false` history is explicitly incomplete.
- A source-level Stage contract is not proof that migrations/backfills ran, WMS is enabled, or production has the same version.

## Legacy order boundary and adjacent changes

`orders allocate/reset-allocation/request-shipping` remain original-order compatibility routes and may affect multiple eligible managed groups. `orders set-delivery-prepared` is LEGACY-only. Their older `SHIPPING_STARTED` readback instructions apply to the order projection, not the new group/Release state machine.

For managed orders, order-number-based administrator memo input now targets the first live group; group execution-property updates target the explicitly selected group. Group memo and historical order memo are not interchangeable. Use the `managementInstruction` in current group detail and inspect a Release snapshot for what was sent to WMS.

`logistics intl-shipment-info DG-...` passes the group number through the existing `orderNo` query. Summary/schema now include nullable `originCountryCode`, `merchantPid`, `nonStandardPid`, `standardPid`, `nsPidSource`. HS code remains the server-resolved SKU override or category fallback. CLI syntax alone does not prove that a group is eligible for international shipment lookup.

## Source provenance

- `commerce-web-platform` stage `bd703fd1e`: `apps/admin/queries/order/delivery-execution/{deliveryExecution,deliveryExecutionCommand,deliveryRelease,deliveryAdjustment,deliveryReconfiguration}.api.ts` and `apps/admin/utils/order/fulfillment-status.ts`.
- `mystarroom-backend` stage `4996c785d`: `commerce/views.py`, `commerce/controller/delivery_execution.py`, request serializers `delivery_execution.py`, `local_delivery_group.py`, `delivery_group_backfill.py`, `cancellation_shipping_quote.py`; `commerce/controller/order.py` rejects legacy preparation for managed orders.
- `makestar-oms` stage `2782aa246`: `DeliveryExecutionController`, `DeliveryLedgerController`, `DeliveryGroupAllocationFailureRecordController`; DTOs under `order/dto/deliveryexecution` and `logistics/dto/IntlShipmentInfoSku.kt`.
- Not exposed by this CLI: internal callbacks, projection republish/reconcile, OMS migration backfill, direct WMS confirmation ingestion and parcel correction/import. Use their separately verified operational workflows; do not substitute the Commerce backfill command.
