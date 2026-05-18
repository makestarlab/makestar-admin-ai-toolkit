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
claude plugin install makestar-admin-skills@makestar-admin-ai-toolkit
```

Add the marketplace without a release tag or `@<ref>`. The unpinned command
above is the expected install path for future updates. Claude Desktop/Claude
Code can still show a stale version if its local marketplace or Desktop session
cache has not refreshed after a release.

If Claude still shows an older version after a release, refresh the marketplace
cache and update the installed plugin:

```bash
claude plugin marketplace remove makestar-admin-ai-toolkit
claude plugin marketplace add makestarlab/makestar-admin-ai-toolkit
claude plugin marketplace update makestar-admin-ai-toolkit
claude plugin update makestar-admin-skills@makestar-admin-ai-toolkit
```

Restart Claude Desktop after updating so the refreshed plugin cache is loaded.

If you installed older releases under the legacy marketplace ID
`makestar-admin`, remove that marketplace/plugin once before reinstalling:

```bash
claude plugin uninstall makestar-admin-skills@makestar-admin
claude plugin marketplace remove makestar-admin
```

The public marketplace name intentionally matches the GitHub repository name so
Claude Desktop/Cowork and Claude Code CLI resolve the same plugin identity.

## Codex marketplace shape

```bash
codex plugin marketplace add makestarlab/makestar-admin-ai-toolkit
codex
# then use /plugins to install and enable makestar-admin-skills
```

## Hermes artifact status

Generated Hermes skills are exported under `hermes/skills/makestar/`.

Current status: `pre-validation`.

Install from a local clone of this public toolkit repository:

```bash
git clone https://github.com/makestarlab/makestar-admin-ai-toolkit.git
cd makestar-admin-ai-toolkit
python installers/hermes/install.py --dry-run
python installers/hermes/install.py --backup
```

`--backup` stores replaced skills under `~/.hermes/skills-backup/` before installing the new copies.

## OpenCode artifact status

Generated OpenCode skills are exported under `opencode/.opencode/skills/`. Optional OpenCode guide/prompt convenience assets may also be present under `opencode/ai-guides/opencode/`, but skills remain the primary installable surface.

Current status: `pre-validation`.

Install from a local clone of this public toolkit repository into the current project:

```bash
git clone https://github.com/makestarlab/makestar-admin-ai-toolkit.git
cd makestar-admin-ai-toolkit
python installers/opencode/install.py --project-root /path/to/your/project --dry-run
python installers/opencode/install.py --project-root /path/to/your/project --backup
```

`--backup` stores replaced skills under `<project>/.opencode/skills-backup/` before installing the new copies.

## Generated version

`0.2.10`
