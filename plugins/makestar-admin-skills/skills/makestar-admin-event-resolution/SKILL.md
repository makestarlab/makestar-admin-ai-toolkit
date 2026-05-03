---
name: makestar-admin-event-resolution
description: Resolve Makestar event code to option/content/SKU/inventory/price using the verified script-first workflow.
version: 0.1.0
author: Makestar Admin Contracts
license: MIT
---

# Makestar Admin Event Resolution

Use this skill when you need to interpret a product event from visible event code down to SKU and inventory.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.3.
Before the first CLI-dependent action, run `makestar-admin --version`, compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Show the documented install path that can provide the required version for this platform, such as macOS `brew install makestarlab/tap/makestar-admin-cli`, Windows `winget install Makestar.MakestarAdminCLI` when current enough, or the public release MSI/archive; then stop until the user updates.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require source-checkout or Python-module fallback commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## Standard flow
1. Pick a visible/reserved event from latest list.
2. Resolve the event by code.
3. Inspect event detail and product contents.
4. Run the helper:
   - `makestar-admin helpers event-option-inventory resolve <event_code>`

## Read results this way
- option sale price = commercial event price
- sku_price / purchase_price = OMS SKU-side price/cost info
- available/total/allocated = stock state
- empty `sku_code` = non-SKU content such as ticket/coupon content

## References
- `references/workflow.md`
