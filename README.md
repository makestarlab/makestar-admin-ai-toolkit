# Makestar Admin AI Toolkit

Public Claude/Codex marketplace distribution and generated Hermes/OpenCode artifact surfaces for Makestar Admin Skills.

This repository is generated. Do not hand-edit generated plugin files here; changes should flow through the toolkit export/publish process. Source provenance is recorded in `PUBLISH_PROVENANCE.json`.

## Runtime boundary

The plugin contains skills, references, and marketplace metadata only. It does not bundle the `makestar-admin` CLI binary. Install the CLI separately before using the skills:

```bash
makestar-admin --version
```

Supported CLI distribution channels remain Homebrew, winget/MSI, and public CLI release artifacts.

## Claude marketplace shape

```bash
claude plugin marketplace add makestarlab/makestar-admin-ai-toolkit
claude plugin install makestar-admin-skills@makestar-admin
```

## Codex marketplace shape

```bash
codex plugin marketplace add makestarlab/makestar-admin-ai-toolkit
codex
# then use /plugins to install and enable makestar-admin-skills
```

## Hermes artifact status

Generated Hermes skills are exported under `hermes/skills/makestar/`.

Current status: `install-supported`.

Reviewable remote install from the release zip:

```bash
VERSION=v0.2.7
ASSET=makestar-admin-ai-toolkit-v0.2.7.zip
EXPECTED_SHA256=<copy from the GitHub release asset digest>
WORKDIR="$(mktemp -d)"
curl -fL "https://github.com/makestarlab/makestar-admin-ai-toolkit/releases/download/${VERSION}/${ASSET}" -o "${WORKDIR}/${ASSET}"
printf '%s  %s\n' "${EXPECTED_SHA256}" "${WORKDIR}/${ASSET}" | shasum -a 256 -c -
unzip -q "${WORKDIR}/${ASSET}" -d "${WORKDIR}/toolkit"
python "${WORKDIR}/toolkit/installers/hermes/install.py" --source-root "${WORKDIR}/toolkit/hermes/skills/makestar" --target "$HOME/.hermes/skills/makestar" --dry-run
python "${WORKDIR}/toolkit/installers/hermes/install.py" --source-root "${WORKDIR}/toolkit/hermes/skills/makestar" --target "$HOME/.hermes/skills/makestar" --backup
```

## OpenCode artifact status

Generated OpenCode skills are exported under `opencode/.opencode/skills/`. Optional OpenCode guide/prompt convenience assets may also be present under `opencode/ai-guides/opencode/`, but skills remain the primary installable surface.

Current status: `install-supported`.

Reviewable remote install from the release zip into the current project:

```bash
VERSION=v0.2.7
ASSET=makestar-admin-ai-toolkit-v0.2.7.zip
EXPECTED_SHA256=<copy from the GitHub release asset digest>
WORKDIR="$(mktemp -d)"
curl -fL "https://github.com/makestarlab/makestar-admin-ai-toolkit/releases/download/${VERSION}/${ASSET}" -o "${WORKDIR}/${ASSET}"
printf '%s  %s\n' "${EXPECTED_SHA256}" "${WORKDIR}/${ASSET}" | shasum -a 256 -c -
unzip -q "${WORKDIR}/${ASSET}" -d "${WORKDIR}/toolkit"
python "${WORKDIR}/toolkit/installers/opencode/install.py" --source-root "${WORKDIR}/toolkit/opencode/.opencode/skills" --project-root "$PWD" --dry-run
python "${WORKDIR}/toolkit/installers/opencode/install.py" --source-root "${WORKDIR}/toolkit/opencode/.opencode/skills" --project-root "$PWD" --backup
```

## Generated version

`0.2.7`
