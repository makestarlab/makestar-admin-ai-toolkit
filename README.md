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

Install from a local clone of this public toolkit repository:

```bash
WORKDIR="$(mktemp -d)"
git clone --depth 1 --branch v0.2.7 https://github.com/makestarlab/makestar-admin-ai-toolkit.git "${WORKDIR}/makestar-admin-ai-toolkit"
cd "${WORKDIR}/makestar-admin-ai-toolkit"
python installers/hermes/install.py --dry-run
python installers/hermes/install.py --backup
```

## OpenCode artifact status

Generated OpenCode skills are exported under `opencode/.opencode/skills/`. Optional OpenCode guide/prompt convenience assets may also be present under `opencode/ai-guides/opencode/`, but skills remain the primary installable surface.

Current status: `install-supported`.

Install from a local clone of this public toolkit repository into the current project:

```bash
WORKDIR="$(mktemp -d)"
PROJECT_ROOT="$PWD"
git clone --depth 1 --branch v0.2.7 https://github.com/makestarlab/makestar-admin-ai-toolkit.git "${WORKDIR}/makestar-admin-ai-toolkit"
cd "${WORKDIR}/makestar-admin-ai-toolkit"
python installers/opencode/install.py --project-root "${PROJECT_ROOT}" --dry-run
python installers/opencode/install.py --project-root "${PROJECT_ROOT}" --backup
```

## Generated version

`0.2.7`
