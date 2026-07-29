<!-- managed:supported_cli_requirement -->
> Requires `makestar-admin` >=0.2.17. Run `makestar-admin --version` before CLI-dependent actions.
> Cowork/sandboxed Linux agents should resolve/install with the generated package helper (`cowork/cowork-cli-bootstrap.sh` in AI Toolkit exports, or `references/cowork-cli-bootstrap.sh` when bundled) and use its verification evidence before CLI actions.
> Host shells keep Homebrew, winget/MSI, or public release archive setup.
<!-- /managed:supported_cli_requirement -->

Operate Makestar order writes only through the verified Stage-only `makestar-admin` workflow.

Use Admin `user_order_number` as the positional identifier, show a dry-run first, and require explicit user authorization for the exact named order set before adding `--env stage --execute --confirm-stage-write`. Complete the documented readback and recovery; never run a live Stage write in unattended CI.
