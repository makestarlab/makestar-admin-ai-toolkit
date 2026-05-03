---
name: makestar-admin-browser-token
description: Recover a Makestar admin bearer token from a live browser session when the Auth CLI path is unavailable.
version: 0.1.0
author: Makestar Admin Contracts
license: MIT
---

# Makestar Admin Browser Token

Use this skill only as the browser fallback when `makestar-admin auth` is unavailable, not logged in and blocked, or independent browser recovery is required. Prefer `makestar-admin-auth-token` first.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.3.
Before the first CLI-dependent action, run `makestar-admin --version`, compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Show the documented install path that can provide the required version for this platform, such as macOS `brew install makestarlab/tap/makestar-admin-cli`, Windows `winget install Makestar.MakestarAdminCLI` when current enough, or the public release MSI/archive; then stop until the user updates.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require source-checkout or Python-module fallback commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## When to use
- `makestar-admin-auth-token` is unavailable or blocked by auth/VPN/browser constraints
- CLI/resource probe returns `401` or `만료된 토큰 입니다` after `makestar-admin auth` refresh attempts
- Need a fresh bearer from an already-authenticated browser session
- Need independent recovery from live browser traffic for incident/debug work

## Procedure
1. Try `makestar-admin-auth-token` first unless the task explicitly requires browser extraction.
2. Confirm browser login at `https://new-admin.makestar.com`.
3. Inspect a recent XHR/fetch request in browser network.
4. Read the current `Authorization: Bearer ...` value.
5. Export it only into the current shell/session:
   - `MAKESTAR_ADMIN_ADMIN_TOKEN`
   - `MAKESTAR_ADMIN_OMS_TOKEN`
6. Do not store the raw token in repo files or commits.

## Remote-user fallback
If the user is remote and cannot do the browser inspection themselves, use Hermes-opened browser tooling to inspect the live network request and reuse that bearer for the current task session.

## Browser login safety
- Agents may navigate the Makestar admin login flow and inspect live browser network requests.
- Password and 2FA/device-approval steps are user-owned steps and must be completed directly by the user.
- Do not type, paste, store, or echo a user's Google password in browser tools, terminal commands, DOM scripts, docs, logs, or tool arguments.
- If a password is disclosed in chat, files, logs, or tool output, treat it as compromised and ask the user to rotate it before continuing.

## References
- `references/auth.md`
