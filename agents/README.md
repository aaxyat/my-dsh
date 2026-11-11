# `/opt/agents` — durable agent workspace

Machine-level workspace required by [`harness/instructions/AGENTS.md`](../harness/instructions/AGENTS.md) §7. This directory is the **source of truth**; `/opt/agents` is the installation target.

```sh
python3 tools/provision_agents.py --dry-run   # inspect
python3 tools/provision_agents.py             # install (locks bin/)
/opt/agents/bin/preflight                     # verify
```

Provisioning is idempotent. It refuses to overwrite a differing installed helper unless `--force`, which unlocks, replaces, and re-locks `bin/`.

## Layout

| Path | Holds | Also |
|---|---|---|
| `/opt/agents/bin` | executable helpers | `chflags uchg` locked after provisioning |
| `/opt/agents/data` | durable, non-regenerable inputs/outputs | `.trash/` for soft deletes |
| `/opt/agents/state` | checkpoints, indexes, resume state, locks | `locks/`, `provision.json` |
| `/opt/agents/logs` | run, job and audit logs | `rm-audit.log`, `retention-audit.log` |
| `/opt/agents/tmp` | scratch and manifests | freely deletable |
| `/opt/agents/tools` | machine-local tool installs (for example `playwright-mcp/`) | provisioned separately; not locked |

Everything is `0700`/`0600`; helpers run with `umask 077`. The workspace is owned by `aaxyat`. There is no root-level alias; always use the absolute `/opt/agents` path.

## Helpers

| Helper | Purpose |
|---|---|
| `preflight` | Structural checks (layout, permissions, helpers, lock, PATH, SSH config, hooks, gitleaks). Exit 1 on FAIL. |
| `manifest --task NAME PATH...` | NUL-delimited manifest with type, size, sha256, symlink target, count and blast radius; writes `/opt/agents/tmp/NAME.manifest` + JSON sidecar. |
| `rm` | Soft-delete shim: scratch is removed; everything else moves to `data/.trash/<date>/<id>/` with an audit line. |
| `gate-rm` | `rm --require-quote`; refuses a deletion without the user's quoted words. |
| `undo-rm <id>` | Restore a soft-deleted batch; `--list` shows ids. |
| `git-snapshot NAME` | Commit tracked **and** untracked work to `refs/backup/NAME-<date>` without touching the index or working tree; `--tar-ignored` archives ignored files. |
| `ssh-probe HOST` | Read-only remote probe: listeners, addresses, `sshd -T`, service state, socket activation. |
| `ssh-verify HOST [CMD]` | Fresh connection bypassing multiplexing; `BatchMode`, `ConnectTimeout=5`. |
| `sshd-apply` | Prints the manual sshd ritual. Its mutating path is **intentionally disabled** until the three rehearsal cases in `AGENTS.md` §4 pass. |
| `retention` | Reports (or with `--apply --quote`, purges) tmp > 7 days, logs and trash > 30 days. Human-owned LaunchAgent should call it. |

Python helpers support `--help`; the shell helpers print usage on a missing argument. Helpers are standalone and use absolute paths, so they do not depend on this repository.

## Soft delete and audit

```sh
/opt/agents/bin/rm --quote "remove stale export" /opt/agents/data/export/
# moved to /opt/agents/data/.trash/2026-11-11/<id>/
/opt/agents/bin/undo-rm --list
/opt/agents/bin/undo-rm <id>
```

- Scratch (`/opt/agents/tmp`, `/tmp/agent-scratch-<uid>`) is removed for real.
- Everything else is moved, with `meta.json` recording the original paths, the quote, the manifest hash (if `--manifest`) and the uid.
- Audit lines are JSON appended to `/opt/agents/logs/rm-audit.log` (`0600`).
- `undo-rm` refuses to overwrite an existing original path.

## Locking

`bin/` is locked with `chflags uchg` so agent code cannot silently modify itself. Any change is a deliberate two-step:

```sh
sudo chflags nouchg /opt/agents/bin/<file>
# edit, then:
chflags uchg /opt/agents/bin/<file>
```

`provision_agents.py --force` performs the unlock/replace/relock sequence. The lock is a speed bump, not a security boundary — the owner can always unlock.

## Activation

The rules expect `/opt/agents/bin` first on `PATH`. This is **not** wired automatically because it edits a shell profile outside the workspace. Add to `~/.zshrc` (or your shell's profile), deliberately:

```sh
export PATH="/opt/agents/bin:$PATH"
```

Until then, call helpers by absolute path and expect `preflight` to report a WARN.

## Retention (human-owned)

Agents never purge. The intended owner is a LaunchAgent; it is not installed by provisioning. Create it yourself after reviewing:

```xml
<!-- ~/Library/LaunchAgents/sh.omp.agents-retention.plist -->
<plist version="1.0"><dict>
  <key>Label</key><string>sh.omp.agents-retention</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/agents/bin/retention</string>
    <string>--apply</string>
    <string>--quote</string>
    <string>scheduled retention per AGENTS.md §7</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer></dict>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>/opt/agents/logs/retention.out.log</string>
  <key>StandardErrorPath</key><string>/opt/agents/logs/retention.err.log</string>
</dict></plist>
```

Then `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/sh.omp.agents-retention.plist`. Installing a LaunchAgent is a host-service change; do it deliberately, not from an agent.

## Security

- No secrets under `/opt/agents`. Reference Keychain items instead.
- Manifests and logs may contain paths and commands; they are `0600` and stay local.
- `rm` never follows a final symlink; a symlink is moved, not its target.
- The workspace is not a sandbox. The Gate in `AGENTS.md` §2 remains the authority.

## Not automated

- Shell `PATH` (edits outside the workspace).
- LaunchAgent installation (human-owned).
- Remote SSH host config and `gitleaks`; see [host readiness](../docs/host-readiness.md).
