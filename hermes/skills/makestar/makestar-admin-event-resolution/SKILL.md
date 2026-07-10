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
Required: `makestar-admin` >=0.2.11.
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
