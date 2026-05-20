# Cowork CLI bootstrap reference

`cowork-cli-bootstrap.sh` is the POSIX shell entrypoint for Claude Desktop Cowork or similar Linux x86_64 agent sandboxes. It resolves `makestar-admin` in this order:

1. trusted absolute `MAKESTAR_ADMIN_CLI_PATH`
2. sandbox-managed `MAKESTAR_ADMIN_CLI_HOME`
3. ordinary `PATH`
4. verified install from the approved public CLI release origin

The helper installs only `makestar-admin-linux-x86_64.zip` from `https://github.com/makestarlab/makestar-admin-cli-releases/releases/download/<tag>/`. It verifies manifest metadata, SHA-256, size, archive layout, safe GitHub release redirects, and `makestar-admin --version` before returning the executable path. It fails closed on unsupported OS/arch, denied network, checksum mismatch, unsafe archive entries, stale managed installs, unsafe manifest versions, or non-canonical URLs.

Plugin and skill artifacts do not bundle the CLI binary. Cowork setup should ship this helper as install support and run it directly with `sh`, not through repo build scripts or package managers.

Example sandbox use:

```sh
export MAKESTAR_ADMIN_CLI_RELEASE_TAG=r2026.05.01
export MAKESTAR_ADMIN_CLI_VERSION=0.2.0
export MAKESTAR_ADMIN_CLI_HOME="$HOME/.makestar-admin/cowork-cli"
CLI_PATH=$(sh ./cowork-cli-bootstrap.sh resolve)
"$CLI_PATH" --version
```

Evidence written to stderr includes the resolved path category, version, approved artifact source, and checksum. It never prints credential values.
