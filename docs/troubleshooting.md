# Troubleshooting

Symptom → likely cause → fix. Commands assume the repository root.

## A profile setting is ignored

**Cause:** the profile patch is layer 4, not the final layer. Home or invocation patches apply after it and can override the same plugin `id`; a bundle may also declare the row later than expected.

**Check:**

1. Search all layers for the row id:

   ```sh
   grep -rn "id: <plugin-id>" ~/.dsh/profiles/*/cordis.patch.yml ~/.dsh/*.yml 2>/dev/null
   ```

2. Confirm the bundle order in `harness/profile/desktop/package.json` — later bundles win.
3. Restart DSH; only HMR-enabled setups apply some changes live.

See [architecture §2](architecture.md#2-profiles-and-composition-order).

## My global instructions are not loaded

**Checks, in order:**

1. Does `~/.agents/AGENTS.md` exist and is it a symlink into this repo?

   ```sh
   ls -l ~/.agents/AGENTS.md
   ./bin/dsh link
   ```

2. Is the working directory inside a project whose root has `.git`? Instructions are discovered from the project root down.
3. Is a project-level `AGENTS.md` overriding the same guidance? More specific wins.
4. Did you create `~/.dsh/AGENTS.md` with identical content? DSH deduplicates identical trimmed content — expected, not a bug.
5. Restart the session; instruction changes are picked up during a session only after file touches, so a brand-new session is the reliable check.

## A skill does not appear

1. Path: `~/.agents/skills/<name>/SKILL.md` (or a flat `~/.agents/skills/<name>.md`).
2. Frontmatter must contain `name` and `description`; the file must start with `---`.
3. Name must be kebab-case and unique enough — a project skill or `~/.dsh/skills` skill with the same name takes precedence (lower rank wins).
4. Symlinks: the loader follows them, but a broken link is invisible.

   ```sh
   ls -l ~/.agents/skills/
   ./bin/dsh doctor
   ```

5. Restart DSH if the watcher missed the change.

## `apply` reports a conflict

**Cause:** the live file differs from the repo and is not backed up-able silently.

Do not reach for `--force` first. Inspect:

```sh
./bin/dsh apply --dry-run
diff -u harness/profile/desktop/cordis.patch.yml ~/.dsh/profiles/desktop/cordis.patch.yml
```

- Live is newer (you changed something in the app): `./bin/dsh capture`, review, commit.
- Repo is newer (you edited it): `./bin/dsh apply --force` (backup is taken automatically).
- Both changed: merge deliberately, then capture/apply.

## A plugin fails to load

1. Version compatibility: the Plugins page shows the requirement. DSH refuses packages whose `engines.dsh`/peers do not match. Use the version-exemption flow only with explicit risk acceptance.
2. Local link installed? `./bin/dsh apply --with-plugins`, then restart.
3. `package.json` must declare `dsh.bundle.patch` and the patch path must exist.
4. Host errors surface in DSH logs; a bundle that fails during `apply()` usually prevents its row from starting. Disable the row in the profile patch to recover, then fix.
5. After editing plugin source, restart (a link does not rebuild anything).

## DSH will not start after a config change

1. Close DSH.
2. Restore the previous profile files:

   ```sh
   ls ~/.dsh/backups/ | tail -1
   cp -R ~/.dsh/backups/my-dsh-<timestamp>/. ~/.dsh/
   ```

3. Or revert the repo commit and `./bin/dsh apply --force`.
4. Start DSH, then bisect the change. A YAML syntax error is the most common cause — run `./bin/dsh check` before applying next time.

## `capture` produces a surprising diff

- DSH or the Settings page rewrote formatting (quotes, ordering): acceptable; commit it separately as `chore(profile): reformat`.
- A plugin install changed `package.json` dependencies: expected; record it in `registry.yaml`.
- A key you expected is missing: `capture` only copies the whitelisted profile files, never credentials or runtime patches.
- Absolute paths changed: profile files should not contain them; if they do, prefer `~` and report it.

## `doctor` cannot find DSH

```sh
ls ~/.dsh/profiles
ls /Applications | grep -i deepseek
```

- If DSH is installed elsewhere, set `DSH_APP` (see `.env.example`).
- If `~/.dsh` is elsewhere, set `DSH_HOME` before running `bin/dsh`.
- `doctor` is diagnostic: missing app/profile yields warnings, not failures.

## `check` passes locally but fails in CI

CI is Linux and runs `./bin/dsh check` with the system `python3`. Differences usually come from:

- case-insensitive macOS filesystem hiding a wrong-case link;
- CRLF or trailing whitespace introduced by an editor;
- files ignored locally by `.gitignore` but referenced by the manifest.

Reproduce with `git ls-files` to confirm the file is actually tracked.

## Model authentication errors after restore

The profile references credentials by variable name. On a new machine:

1. Confirm the key exists in DSH Settings → Account, or in the environment that launched the app.
2. The name must match exactly (`OPENCODE_GO_API_KEY`), including case.
3. A GUI app does **not** inherit your shell's exports if launched from Finder — start it from a terminal to test, or re-enter the key in Settings.

## `command not found: python3`

`bin/dsh` looks for the Python bundled with DSH (`~/.dsh/dsh-runtimes/*/dependencies/python/bin/python3`) and then `python3` on `PATH`. If neither exists, install the Xcode Command Line Tools (`xcode-select --install`) or set `DSHCTL_PYTHON=/path/to/python3`.
