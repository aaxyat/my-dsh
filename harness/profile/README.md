# Profile — `desktop`

The composed DSH profile for this machine. Captured from `~/.dsh/profiles/desktop` and deployed back by `./bin/dsh apply`.

| File | Purpose | Notes |
|---|---|---|
| `cordis.patch.yml` | Patch layer: providers, models, UI, agent loop, tool settings | Edited by the DSH Settings page too — run `capture` after changing settings |
| `package.json` | `dsh.profile.bundles` (ordered) and plugin dependencies | Later bundles win; plugin installs modify this file |
| `pnpm-workspace.yaml` | pnpm linker + `allowBuilds` | Keep in sync with plugin build approvals |

`cordis.yml` in the live profile is a generated empty skeleton and is deliberately not managed here.

## Composition

1. `@deepseek-ai/dsh-base`
2. `@deepseek-ai/dsh-web-app`
3. …additional bundles in declared order
4. `cordis.patch.yml` (this directory)
5. home/invocation patches (written by the app; higher priority)

See [../../docs/architecture.md](../../docs/architecture.md#2-profiles-and-composition-order).

## Changing it

- **From the app:** change the setting → `./bin/dsh capture` → review diff → commit.
- **From the repo:** edit `cordis.patch.yml` → `./bin/dsh check` → `./bin/dsh apply` → restart if needed.

Never store credentials here. Providers reference keys by environment variable name (`apiKeyEnv`).

## Adding another profile

If a future machine uses a different profile (e.g. `work`), create `harness/profile/work/` with the same three files, add its artifacts to `harness/manifest.json`, and set `"profile": "work"` — or keep both and make the profile selectable. The tool applies the profile named in the manifest.
