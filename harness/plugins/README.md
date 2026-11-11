# Plugins

Two very different things are tracked here:

| Kind | Location | Deployed? |
|---|---|---|
| **Personal bundle** (source you own) | `harness/plugins/<name>/` | Yes, as a `link:` dependency via `./bin/dsh apply --with-plugins` |
| **Third-party bundle** (npm/Git) | only recorded in [`registry.yaml`](registry.yaml) | Reinstalled from its source; never vendored |

## Personal bundle anatomy

Use [`pinned-workspaces/`](pinned-workspaces/) as the reference implementation for a hand-written
bundle. [`btw/`](btw/) is the reference for a TypeScript bundle: it commits its built `lib/` output
so installation needs no Node toolchain. See [btw/README.md](btw/README.md) for its build and test
commands. The `*-mcp/` bundles ([`parallel-mcp/`](parallel-mcp/), [`playwright-mcp/`](playwright-mcp/),
[`context7-mcp/`](context7-mcp/), [`cloudflare-mcp/`](cloudflare-mcp/)) are **configuration-only**:
they ship no Host or Client entry, only a patch that inserts an MCP client row. Use that shape when
an MCP server must be installed into an already-running app.

```
<name>/
├── package.json        # dsh.bundle.patch, optional dsh.client, exports
├── cordis.patch.yml    # the row(s) this bundle inserts
├── index.js            # host half: export function apply(ctx) {}
├── client.js           # optional UI half (window.__ModuleLoader__.load)
├── locale/*.json       # optional UI strings
└── icon.svg            # optional
```

Minimum `package.json` shape:

```json
{
  "name": "@local/<name>",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "exports": { ".": "./index.js", "./client": "./client.js" },
  "dsh": {
    "bundle": { "patch": "./cordis.patch.yml" },
    "client": { "platform": "web", "immediately": true, "inject": ["..."] }
  }
}
```

The patch usually just inserts the row:

```yaml
- insert:
    - id: <name>
      name: '@local/<name>'
```

## Adding a personal plugin

1. Create the directory and files above.
2. Add it to `harness/manifest.json` → `plugins`, with `"install": "link"` and `"enabled": false`.
3. Test it:

   ```sh
   ./bin/dsh apply --dry-run --with-plugins
   ./bin/dsh apply --with-plugins     # pnpm add link:<repo>/harness/plugins/<name>
   ```

4. Restart DSH, verify the Plugins page shows it loaded, then flip `"enabled": true` in the manifest and commit.

`apply --with-plugins` edits `package.json` (adds the dependency and appends the bundle name to `dsh.profile.bundles`). Run `./bin/dsh capture` afterwards so the repo records what the live profile actually contains.

## Security

Host-half plugin code runs **in-process, outside the workspace sandbox**, with the user's privileges. Review anything before enabling it; treat a third-party bundle like installing a binary. A plugin's `engines.dsh`/peer requirements must match the running DSH version.

## Removing a plugin

1. Disable/remove it in the DSH Plugins page (preferred — it edits the profile correctly).
2. `./bin/dsh capture`, then move the personal source to `harness/plugins/_archive/<name>/` or delete it in a dedicated commit.
3. Remove its manifest entry and registry row.

Archived plugins keep their history in Git; there is no need to keep dead directories in the active tree.
