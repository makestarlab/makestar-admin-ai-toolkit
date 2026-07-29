---
name: makestar-admin-order-writes
description: Safely run verified Stage-only stock allocation, shipping request, and delivery-prepared order writes.
version: 0.1.0
author: Makestar Admin Contracts
license: MIT
---

# Makestar Admin Order Writes

Use this skill only for the four verified order write workflows: stock allocation, allocation reset, shipping request create/cancel, and delivery-prepared set/unset.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.17.
Cowork/sandboxed Linux agents: before any CLI action, resolve or install the sandbox CLI with the generated package helper (`cowork/cowork-cli-bootstrap.sh` in AI Toolkit exports, or `references/cowork-cli-bootstrap.sh` when that helper is bundled next to these instructions), then use the returned executable path and its verification evidence. Do not use host installers inside the sandbox.
Host shells: use the normal `makestar-admin` on PATH and keep macOS Homebrew, Windows winget/MSI, Linux `install.sh`, or public release archive install guidance available for operator setup.
Before the first CLI-dependent action, run `makestar-admin --version` (or the Cowork helper returned executable with `--version`), compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Agents may attempt exactly one approved automatic install/upgrade for the detected host OS, then rerun `makestar-admin --version`.
  - macOS host: run `brew update && (brew upgrade makestarlab/tap/makestar-admin-cli || brew install makestarlab/tap/makestar-admin-cli)`.
  - Windows host PowerShell: run `winget upgrade --id Makestar.MakestarAdminCLI -e --source winget; if ($LASTEXITCODE -ne 0) { winget install --id Makestar.MakestarAdminCLI -e --source winget }`.
  - Linux host: run `curl -fsSL https://github.com/makestarlab/makestar-admin-cli-releases/releases/latest/download/install.sh | sh`.
  - Cowork/sandboxed Linux: use the generated package helper and its verification evidence, not host package managers.
  If the approved command needs admin elevation, opens a GUI installer, fails, or still leaves the CLI outside the required range, stop and show the relevant manual setup path: Homebrew on macOS, winget or the public MSI on Windows, or the public release `install.sh`/archive on Linux.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require repository fallback or Python-module commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## Non-negotiable safety boundary

- Every command defaults to dry-run. Dry-run needs no authentication.
- There is no production execution path. All actual writes are restricted to the fixed integrated-admin Stage origin.
- Do not add or suggest `--allow-prod`.
- Before an actual write, show the dry-run JSON and obtain explicit user authorization for the exact named order set and operation.
- An actual write must include exactly `--env stage --execute --confirm-stage-write`.
- Start a new workflow with one dedicated Stage order first. Expand to a batch only after its complete round trip is verified.
- Do not run live Stage writes in unattended CI.

## Identifier contract

The positional identifier for all four commands is Admin `user_order_number`.

- OMS `orderNo` / `orderNoList` is the same string as Admin `user_order_number`.
- The Admin delivery-prepared payload calls the array `order_number_list`; it still contains `user_order_number` values.
- Do not use `user_order_no`; that name is not the Admin field.
- Never use Admin `order_number` (식별번호) for these commands.
- Multiple values are separated by spaces, not commas. Duplicate values are rejected.

The examples use descriptive fixture aliases, not real identifiers:

- `STAGE-OMS-ROUNDTRIP-20260724-001`
- `STAGE-ADMIN-DELIVERY-PREPARED-20260724-001`

Always replace an alias with a preflight-confirmed, dedicated Stage `user_order_number`. Never execute the literal alias.

## Dry-run first

```bash
makestar-admin orders allocate STAGE-OMS-ROUNDTRIP-20260724-001 --json
makestar-admin orders reset-allocation STAGE-OMS-ROUNDTRIP-20260724-001 --json
makestar-admin orders request-shipping STAGE-OMS-ROUNDTRIP-20260724-001 --create --json
makestar-admin orders request-shipping STAGE-OMS-ROUNDTRIP-20260724-001 --cancel --json
makestar-admin orders set-delivery-prepared STAGE-ADMIN-DELIVERY-PREPARED-20260724-001 --prepared --json
makestar-admin orders set-delivery-prepared STAGE-ADMIN-DELIVERY-PREPARED-20260724-001 --not-prepared --json
```

For a real approved Stage order, append the execution gate:

```text
--env stage --execute --confirm-stage-write
```

## Allocation round trip

Before allocation, record the dedicated fixture baseline: eligible OMS order status, `READY` delivery status, absence of allocation/order-SKU/WMS markers, KitTree mapping, and exact available/allocated stock quantities.

1. Dry-run and then, after exact authorization, run `makestar-admin orders allocate <user_order_number>`.
2. Read back OMS allocation markers, order-SKU rows, delivery status, and exact SKU stock.
3. Run `makestar-admin orders reset-allocation <user_order_number>` only for state that readback shows must be reset.
4. Verify allocation/WMS markers are removed and exact stock quantities match the recorded baseline.

Allocation and reset summaries deliberately remain `verified=false`; command success is not final-state verification. The synchronous allocation batch is transactional for an NCM transport failure or business rejection, but an eligibility response can still contain per-order success and failure rows. Drive reset and recovery from readback, not only from the exit code or response list.

## Shipping-request round trip

`배송요청` is the OMS/WMS release instruction. It is not the Admin `배송준비` boolean/time.

1. Record the allocated `READY` baseline and WMS release-registration marker.
2. Run `makestar-admin orders request-shipping <user_order_number> --create`.
3. Require an exact success set, then read back `SHIPPING_STARTED` and the WMS marker.
4. Run `makestar-admin orders request-shipping <user_order_number> --cancel`.
5. Require an exact success set, then read back `READY` and the restored marker baseline.

Both create and cancel summaries remain `verified=false` and require readback. A successful create also requires cancellation/recovery before the workflow is complete.

## Delivery-prepared round trip

`배송준비` is the Admin `delivery_requested` boolean/timestamp. It is not OMS/WMS `배송요청`, and it does not create the OMS `READY` prerequisite.

1. Record the explicit boolean and timestamp baseline.
2. Run `makestar-admin orders set-delivery-prepared <user_order_number> --prepared`.
3. The CLI automatically reads back exactly one matching Admin order and verifies `true` plus a timestamp.
4. Run `makestar-admin orders set-delivery-prepared <user_order_number> --not-prepared`.
5. The CLI automatically verifies `false` plus a cleared timestamp.

An originally absent delivery-request object cannot be restored byte-for-byte by writing an explicit false/null object. Treat that as semantic restoration unless an explicit baseline was recorded.

## Failure handling

- On transport failure, schema drift, partial success, or nonzero exit, treat mutation state as unknown until readback completes.
- Never blindly retry a write.
- Recover only the orders whose readback differs from the recorded baseline.
- Escalate to manual cleanup when the baseline cannot be proven or restored.
