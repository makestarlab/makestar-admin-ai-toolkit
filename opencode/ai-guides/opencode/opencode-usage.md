# Optional Makestar guides for OpenCode

<!-- managed:supported_cli_requirement -->
> Requires `makestar-admin` >=0.2.16. Run `makestar-admin --version` before CLI-dependent actions.
> Cowork/sandboxed Linux agents should resolve/install with the generated package helper (`cowork/cowork-cli-bootstrap.sh` in AI Toolkit exports, or `references/cowork-cli-bootstrap.sh` when bundled) and use its verification evidence before CLI actions.
> Host shells keep Homebrew, winget/MSI, or public release archive setup.
<!-- /managed:supported_cli_requirement -->

Primary install surface: generated OpenCode skills under `.opencode/skills/<skill>/SKILL.md`.
These guides and prompts are convenience references only; OpenCode skill installability does not depend on copying them.

Available prompts:
- `prompts/makestar-auth-token.md`
- `prompts/makestar-browser-token.md`
- `prompts/makestar-resource-scripts.md`
- `prompts/makestar-event-resolution.md`
- `prompts/makestar-read-only-query.md`
- `prompts/makestar-order-writes.md`

Start with `makestar-read-only-query` for operator lookup tasks.
Use `makestar-auth-token` before browser-token extraction when scripts need a bearer token.
Use `makestar-resource-scripts` when you need the broader contract/query surface.
Use `makestar-order-writes` only for explicitly authorized, Stage-only order mutations after showing a dry-run.
