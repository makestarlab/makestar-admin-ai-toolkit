---
name: makestar-admin-auth-token
description: Acquire and stage Makestar integrated-admin bearer tokens with the makestar-admin auth CLI before falling back to browser extraction.
version: 0.1.0
author: Makestar Admin Contracts
license: MIT
---

# Makestar Admin Auth Token

Use this skill when Makestar admin resource scripts need a valid bearer token and the integrated `makestar-admin auth` CLI is available. This is the preferred path before browser network-token extraction.

## CLI preflight
<!-- managed:cli-preflight -->
Required: `makestar-admin` >=0.2.4.
Before the first CLI-dependent action, run `makestar-admin --version`, compare it with the required range, then print exactly one status line:
- `CLI update required` — if the CLI is missing, older than the minimum, or outside the supported range. Show the documented install path that can provide the required version for this platform, such as macOS `brew install makestarlab/tap/makestar-admin-cli`, Windows `winget install Makestar.MakestarAdminCLI` when current enough, or the public release MSI/archive; then stop until the user updates.
- `skill/plugin update required` — if the installed CLI is newer than this skill bundle supports and a newer skill bundle is available. Do not downgrade silently.
- `check auth/setup` — only when the CLI is in range; then run `makestar-admin auth status` if the action still fails.
Installed skills/plugins do not bundle the CLI binary. Do not require source-checkout or Python-module fallback commands from an installed skill/plugin bundle.
<!-- /managed:cli-preflight -->

## When to use
- Need `MAKESTAR_ADMIN_ADMIN_TOKEN` / `MAKESTAR_ADMIN_OMS_TOKEN` for read-only CLI/resource probes.
- The shell token is missing, stale, or expired.
- The operator has already completed auth login before.
- You want refresh/access-token caching instead of manually extracting a browser XHR bearer.

## Procedure
2. Check login state without printing secrets:
   ```bash
   makestar-admin auth status
   ```
3. If not logged in, run:
   ```bash
   makestar-admin auth login
   ```
   - The browser/password/2FA/device-approval steps are user-owned.
   - Do not type, paste, store, or echo the user's Google password.
4. Stage token env vars for the current terminal session only. First identify the shell the agent is actually using; Git for Windows often provides Git Bash, but Claude/Codex on Windows may run PowerShell instead.

   macOS / Linux / Git Bash:
   ```bash
   eval "$(makestar-admin auth token --shell)"
   ```

   Windows PowerShell:
   ```powershell
   $tokens = makestar-admin auth token --json | ConvertFrom-Json
   $env:MAKESTAR_ADMIN_ADMIN_TOKEN = $tokens.MAKESTAR_ADMIN_ADMIN_TOKEN
   $env:MAKESTAR_ADMIN_OMS_TOKEN = $tokens.MAKESTAR_ADMIN_OMS_TOKEN
   ```

   Plain `cmd.exe` is not recommended for agent runs; prefer PowerShell or Git Bash.
5. Verify with read-only probes using the unified CLI:
   ```bash
   makestar-admin product-events latest --display-status displayed --size 1
   makestar-admin skus search --size 1
   ```

## Credential and output rules
- Default credential store: `~/.makestar-admin/credentials.json`.
- `MAKESTAR_ADMIN_AUTH_STORE` is only for tests/temp stores.
- Refresh tokens and access tokens are both secrets.
- Do not print raw `--raw`, `--json`, PowerShell token objects, callback URLs, credential files, or shell exports in chat/logs/docs.
- Use `token --shell` only in POSIX-compatible shells; use `token --json` only to populate PowerShell env vars without displaying the values.
- Do not commit credential stores or generated token captures.

## Cache/refresh notes
- Cached access tokens are reused until shortly before expiry.
- Refresh responses may omit `expires_in`; the CLI falls back to the access-token JWT `exp` only for expiry calculation.
- JWT parsing is not signature validation and not an authorization decision.

## Browser fallback
Use `makestar-admin-browser-token` only when the `makestar-admin auth` path is unavailable, not logged in and blocked, or independent browser recovery is explicitly needed.

## References
- `references/auth-cli.md`
