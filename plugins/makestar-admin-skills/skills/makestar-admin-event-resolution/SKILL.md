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
- First check whether the separately installed CLI is available: `makestar-admin --version`.
- If missing, guide the user to install it: macOS `brew install makestarlab/tap/makestar-admin-cli`; Windows `winget install Makestar.MakestarAdminCLI`; otherwise use the public release MSI/archive.
- Installed skills/plugins do not bundle the CLI binary. Do not require a source checkout, `.venv`, `uv`, `PYTHONPATH`, or Python module fallback from an installed skill/plugin bundle.

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
