<!-- managed:supported_cli_requirement -->
> Requires `makestar-admin` >=0.2.11. Run `makestar-admin --version` before CLI-dependent actions.
> Cowork/sandboxed Linux agents should resolve/install with the generated package helper (`cowork/cowork-cli-bootstrap.sh` in AI Toolkit exports, or `references/cowork-cli-bootstrap.sh` when bundled) and use its verification evidence before CLI actions.
> Host shells keep Homebrew, winget/MSI, or public release archive setup.
<!-- /managed:supported_cli_requirement -->

Refresh the Makestar admin browser bearer token for the current session.

Use this only as a fallback when the integrated `makestar-admin auth` flow is unavailable. Do not store raw tokens in repo files or commits.
