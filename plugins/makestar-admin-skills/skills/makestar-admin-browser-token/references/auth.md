Use this bundled reference when browser token refresh is needed for the current operator session.

- Prefer the integrated `makestar-admin auth` flow when it is available.
- Use browser token extraction only as a fallback for read-only investigation.
- Keep admin and OMS tokens scoped to the current terminal session.
- Never store raw bearer tokens in repository files, generated bundles, or chat logs.
