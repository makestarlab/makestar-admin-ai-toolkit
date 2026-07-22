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
Required: `makestar-admin` >=0.2.15.
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

## When to use
- Need `MAKESTAR_ADMIN_ADMIN_TOKEN` / `MAKESTAR_ADMIN_OMS_TOKEN` for read-only CLI/resource probes.
- The shell token is missing, stale, or expired.
- The operator has already completed auth login before.
- You want refresh/access-token caching instead of manually extracting a browser XHR bearer.

## Procedure
1. Use the integrated `makestar-admin auth` command from the resolved CLI binary or console entrypoint. Installed skill/plugin bundles must not fall back to repository module commands when `makestar-admin` is unavailable.
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
- Cowork auth may use exactly one of these safe paths: a CLI-managed credential store inside the sandbox, a pre-provisioned `MAKESTAR_ADMIN_ADMIN_TOKEN` env var, or `MAKESTAR_ADMIN_AUTH_STORE` pointing at an explicit sandbox-accessible credential store chosen by the operator/user.
- `MAKESTAR_ADMIN_AUTH_STORE` is a real operator/user override for sandbox-accessible stores when the default home path is not appropriate; it is not limited to tests/temp stores.
- Refresh tokens and access tokens are both secrets.
- Do not print raw `--raw`, `--json`, PowerShell token objects, callback URLs, credential files, or shell exports in chat/logs/docs.
- Use `token --shell` only in POSIX-compatible shells; use `token --json` only to populate PowerShell env vars without displaying the values.
- In Cowork, do not display `token --raw`, `token --json`, or `token --shell` output; evaluate/assign it only inside the terminal session that will run the probes.
- Do not commit credential stores or generated token captures.

## Cache/refresh notes
- Cached access tokens are reused until shortly before expiry.
- Refresh responses may omit `expires_in`; the CLI falls back to the access-token JWT `exp` only for expiry calculation.
- JWT parsing is not signature validation and not an authorization decision.

## Browser fallback
Use `makestar-admin-browser-token` only when the `makestar-admin auth` path is unavailable, not logged in and blocked, or independent browser recovery is explicitly needed.

## References
- `references/auth-cli.md`
