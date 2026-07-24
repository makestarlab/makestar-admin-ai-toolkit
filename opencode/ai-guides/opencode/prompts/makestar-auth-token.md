<!-- managed:supported_cli_requirement -->
> Requires `makestar-admin` >=0.2.16. Run `makestar-admin --version` before CLI-dependent actions.
> Cowork/sandboxed Linux agents should resolve/install with the generated package helper (`cowork/cowork-cli-bootstrap.sh` in AI Toolkit exports, or `references/cowork-cli-bootstrap.sh` when bundled) and use its verification evidence before CLI actions.
> Host shells keep Homebrew, winget/MSI, or public release archive setup.
<!-- /managed:supported_cli_requirement -->

Acquire Makestar integrated-admin tokens with `makestar-admin auth`.

Prefer this before browser network-token extraction. Do not print raw tokens, credential files, or callback URLs containing sensitive values.
