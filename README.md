# Makestar Admin AI Toolkit

Public Claude/Codex marketplace distribution for Makestar Admin Skills.

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

## Generated version

`0.2.7`
