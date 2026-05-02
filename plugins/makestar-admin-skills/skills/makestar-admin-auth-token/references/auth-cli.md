# Auth CLI Token Acquisition

## Commands

Preferred integrated CLI path. Do not require the source repo, `.venv`, or `uv` when the `makestar-admin` binary/console entrypoint is available:

```sh
makestar-admin auth status
makestar-admin auth login --auth-base-url https://auth.makestar.com
```

Stage tokens in the current terminal only. Match the command to the shell that the agent is actually using. Git for Windows provides Git Bash, but Windows agent sessions may still be PowerShell.

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

## Export contract

`token --shell` exports current-session env vars expected by resource scripts:

```text
MAKESTAR_ADMIN_ADMIN_TOKEN
MAKESTAR_ADMIN_OMS_TOKEN
```

Do not print the actual token output in chat/logs/docs. Evaluate or assign it directly into the terminal session that will run the resource probes.

## Credential store

Default:

```text
~/.makestar-admin/credentials.json
```

Properties:
- stdlib-only JSON file store
- directory/file permissions best-effort private mode
- contains secrets; never commit or copy into generated skill bundles
- `MAKESTAR_ADMIN_AUTH_STORE` may override path for tests/temp smoke only

## Live endpoint nuance

The verified refresh endpoint used by the CLI is:

```text
https://auth.makestar.com/apis/user/registration/token_refresh/
```

The shorter path below returned 404 in live testing and should not be used:

```text
https://auth.makestar.com/registration/token_refresh/
```
