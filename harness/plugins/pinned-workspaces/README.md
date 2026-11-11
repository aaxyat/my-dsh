# @local/pinned-workspaces

Personal DSH Web bundle that keeps frequently used workspaces at the top of the sidebar and one click away.

| Field | Value |
|---|---|
| Package | `@local/pinned-workspaces` |
| Version | `1.0.0` |
| Kind | personal bundle, client-only |
| Bundle patch | `cordis.patch.yml` inserts row `pinned-workspaces` |
| Installed | yes — `desktop` profile, linked from this directory |
| Source of truth | this directory (the pre-repo copy at `~/Documents/Projects/Deepseek/pinned-workspaces` is now only a legacy duplicate) |

## What it does

- Adds **Pin workspace / Unpin workspace** to the Workspace context menu (right-click and the row's `...` menu).
- Adds a **sidebar-foot toggle** that opens a floating quick-access panel of pinned workspaces.
- Moves a pinned workspace to the front of the sidebar list, mirroring how a pinned session leads its row.
- Persists the pin set in the browser under `dsh.pinned.workspaces.v1`, next to the sidebar's own view state.

## Files

| File | Role |
|---|---|
| `package.json` | package metadata, `dsh.bundle.patch`, client entry and injected client services |
| `cordis.patch.yml` | inserts the `pinned-workspaces` row into the composition |
| `index.js` | host half — intentionally a no-op (`export function apply() {}`); the feature lives in the client |
| `client.js` | UI: context-menu action, sidebar toggle, floating panel, ordering |
| `locale/en.json`, `locale/zh.json` | bundle title/description shown in the Plugins page |
| `icon.svg` | bundle icon |

## Install and update

```sh
./bin/dsh apply --with-plugins     # pnpm add link:<repo>/harness/plugins/pinned-workspaces
# restart DSH
```

`bin/dsh` appends the bundle to `dsh.profile.bundles` only if it is not already selected, then `capture` records the resulting dependency in `machine/inventory.json`.

Editing `client.js` requires a DSH restart: a `link:` dependency is not rebuilt or hot-reloaded from this repository.

## Disable or remove

Disable it in the DSH **Plugins** page (preferred; it updates the profile patch/bundle list), then:

```sh
./bin/dsh capture          # record the new profile state
git commit -am "chore(plugins): disable pinned-workspaces"
```

To remove it entirely, remove the bundle selection and dependency in the app, capture, then delete this directory in a dedicated commit. The legacy directory outside the repo can be archived at the same time.

## Provenance

Created 2026-11-11 alongside the harness repository bootstrap. Originally written in `~/Documents/Projects/Deepseek/pinned-workspaces`, copied here as the canonical source, and the live profile link was repointed at this copy on 2026-11-11.

## Security

Client-only: no host code, no network calls, no credentials. It reads the workspace list through injected client services and stores only workspace ids in browser storage.
