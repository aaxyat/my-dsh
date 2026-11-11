# Workflow — changing the harness safely

Two directions, one loop:

```
        DSH app / live config
                │  capture
                ▼
            this repo  ── commit ──▶ GitHub
                │  apply
                ▼
        this or another machine
```

Rule of thumb: **the repo is edited deliberately, the live machine is captured deliberately, and every transition is a reviewable diff.**

## The loop

```sh
# 1. See where you are
./bin/dsh doctor
git status --short

# 2. Make the change (one direction only)
#    a) change a setting in the DSH app  -> ./bin/dsh capture
#    b) edit a repo file                 -> ./bin/dsh apply

# 3. Validate
./bin/dsh check
./bin/dsh apply --dry-run     # if deployment is involved
git diff                      # read it, really

# 4. Record and publish
git add -A
git commit -m "feat(profile): add <thing>"
git push

# 5. Update HANDOFF if the session changed state or decisions
```

If `capture` and `apply` disagree about a file, **stop**. The live file was changed by the app after the last capture, or the repo was edited without applying. Decide explicitly which side is authoritative and record why in `HANDOFF.md`.

## Recipes

### Change a setting in the app

1. Change it in DSH.
2. `./bin/dsh capture` — copies the live profile files into `harness/profile/desktop/`.
3. `git diff harness/profile` — confirm only the intended keys changed.
4. `git commit -m "feat(profile): ..."`.

### Change the profile from the repo

1. Edit `harness/profile/desktop/cordis.patch.yml`.
2. `./bin/dsh check` for syntax and references.
3. `./bin/dsh apply --dry-run`, then `./bin/dsh apply`.
4. Restart DSH if the change touches host plugins; HMR may apply UI changes live.

### Add a personal skill

```sh
mkdir -p harness/skills/my-skill
$EDITOR harness/skills/my-skill/SKILL.md   # start from docs/templates/SKILL.md
./bin/dsh check
./bin/dsh link                             # ~/.agents/skills/my-skill -> repo
```

Open a new DSH session and confirm the skill appears in the catalog / `skill` tool. Skills are directory bundles: `SKILL.md` plus optional `references/` and `scripts/`. Keep `SKILL.md` under ~8 KB; the body is loaded on invocation.

### Add a personal plugin (bundle)

1. Create `harness/plugins/<name>/` from an existing bundle (`harness/plugins/pinned-workspaces/` is the reference).
2. Required files: `package.json` with `dsh.bundle.patch`, the patch file, and `index.js` exporting `apply(ctx)`; add `client.js` for UI work.
3. Add the plugin to `harness/manifest.json` under `plugins` with `"install": "link"` and `"enabled": false` until proven.
4. Dry-run, install, restart:

   ```sh
   ./bin/dsh apply --dry-run --with-plugins
   ./bin/dsh apply --with-plugins
   ```

5. Confirm it loads (no error in the Plugins page), then set `"enabled": true` in the manifest and commit.

Host plugin code runs in-process outside the workspace sandbox — review any third-party code before enabling it.

### Add a third-party plugin

1. Install/enable it in the DSH Plugins page.
2. `./bin/dsh capture` — updates `machine/inventory.json` with the installed bundle and version.
3. Add an entry to `harness/plugins/registry.yaml` (name, version, source, why).
4. Commit both. Never vendor the package.

### Add an MCP server

1. Add a `dsh-mcp-client` row to `harness/profile/desktop/cordis.patch.yml` (see [architecture](architecture.md#7-mcp-servers)).
2. Add the same server to `harness/mcp/servers.yaml`.
3. Reference credentials by environment variable, never inline.
4. `./bin/dsh check`, `apply`, restart, verify the `mcp__<server>__*` tools appear.

### Update DSH itself

1. Capture **before** upgrading and commit (rollback point).
2. Upgrade the app.
3. `./bin/dsh capture`; review any rewritten profile keys.
4. `check`, `doctor`, open a session, verify instructions + skills + plugins.
5. Commit as `chore(dsh): upgrade to <version>` and record it in `HANDOFF.md`.

### Recover from a bad change

```sh
git log --oneline -- harness/profile/desktop/cordis.patch.yml
git revert <commit>              # revert the repo
./bin/dsh apply --force          # redeploy; live file is backed up first
```

Backups from `apply` live in `~/.dsh/backups/my-dsh-<timestamp>/`.

## Commit conventions

- Conventional Commits: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `security`.
- Scope the area when useful: `feat(profile):`, `docs(skills):`, `chore(scripts):`.
- Subject imperative, ≤ 72 characters; body explains *why* and any risk.
- One logical change per commit. Never mix a capture of unrelated settings with a feature.
- Reference ADRs (`ADR-0002`) when a change implements a recorded decision.

## What must be updated together

| Change | Also update |
|---|---|
| Any deployed artifact | `harness/manifest.json` |
| New/renamed file or directory | `docs/layout.md` if the pattern changes |
| Structural decision | new ADR + link from `HANDOFF.md` |
| User-visible behaviour | `CHANGELOG.md` under `[Unreleased]` |
| Machine state/versions | `machine/inventory.json` (via capture) |
| Anything at all | `HANDOFF.md` session log at session end |

## Automation

CI (`.github/workflows/validate.yml`) runs `./bin/dsh check` on every push and pull request. `check` is repo-only: it never reads `~/.dsh`, so it works on a clean runner. Machine-dependent verification stays local in `doctor` and `apply --dry-run`.
