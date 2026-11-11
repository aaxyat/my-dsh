# Host readiness — global agent rules

Audit of the assumptions in [`harness/instructions/AGENTS.md`](../harness/instructions/AGENTS.md) and [`RULES.md`](../harness/instructions/RULES.md) against the current machine.

| | |
|---|---|
| Audited | 2026-11-11 |
| Host | Mac16,1 · arm64 · Darwin 27.0.0 |
| DSH | desktop `0.2.2-rc.1`, profile `desktop` |
| `/opt/agents` | Provisioned from [`agents/`](../agents/README.md); 10 helpers, `0700`, `bin/` locked |
| Verdict | **Workspace ready; remote-host and hook integrations still missing.** `preflight` exits 0 with 7 warnings. |

## Provisioned workspace

`python3 tools/provision_agents.py` created the layout and installed the helpers from the tracked `agents/` tree. `state/provision.json` records the source commit and per-helper hashes.

| Rule assumption | Observed | Action |
|---|---|---|
| Layout `bin/data/state/logs/tmp` with `.trash`, `locks/` | Present, `0700`, owner `aaxyat` | None |
| `/opt/agents` is `0700` | `drwx------` | None |
| `bin/` and every helper locked with `chflags uchg` | Locked and verified by `preflight` | Unlock deliberately to change |
| Helpers exist and are executable | 10/10 | None |
| `/agents` symlink alias | **Missing** — `/opt` is root-owned and sudo is not passwordless | `sudo ln -s /opt/agents /agents` manually |
| `bin/` first on `PATH` | **Not wired** — provisioning does not edit shell profiles | Add `export PATH="/opt/agents/bin:$PATH"` yourself |
| Retention LaunchAgent | **Not installed** — deliberately human-owned | Review and install from `agents/README.md` |

## Helpers — implemented and smoke-tested

| Helper | Status | Evidence |
|---|---|---|
| `preflight` | Works; exit 0 with warnings | Full run on 2026-11-11 |
| `manifest` | Works | Generated a 2-entry manifest with sizes, hashes, NUL records, JSON sidecar, `0600` |
| `rm` | Works; soft-deletes, audits, guards `bin/` and protected roots | Scratch purge, soft delete + undo, locked-helper refusal |
| `gate-rm` | Works | Refuses without `--quote` (exit 2) |
| `undo-rm` | Works | Listing and restoring a batch; refuses to overwrite |
| `git-snapshot` | Works | Temp repo: tracked + untracked in `refs/backup/`, index/worktree untouched, ignored tar |
| `retention` | Works; dry run and `--apply --quote` | Purged an aged tmp file and logged the audit line |
| `ssh-probe` / `ssh-verify` | Usage and guard paths verified only | **No SSH config exists, so no host was contacted** |
| `sshd-apply` | Plan only; mutating path **disabled** | Refuses to execute until the three rehearsals pass |

Smoke-test artifacts were removed; only audit lines remain in `/opt/agents/logs/`.

## Remote hosts

| Rule assumption | Observed | Impact |
|---|---|---|
| `~/.ssh/config` defines `newton` and `mediaserver` | **No `~/.ssh/config`**; only `known_hosts` and an `agent/` directory | Host aliases and `ControlPersist` rules cannot be exercised |
| Bitwarden SSH agent is the auth path | Socket `~/.bitwarden-ssh-agent.sock` exists, but `SSH_AUTH_SOCK` points at `/var/run/com.apple.launchd.../Listeners` | Agent auth will not use Bitwarden until the variable is set |
| `ControlPersist 3m`, off for `mediaserver` | Not configured | The multiplexing-bypass risk described in §4 is absent for now |
| Keychain item `newton-sudo` | Not verified | Do not rely on it until tested |
| `sudo -S` can pipe a Keychain secret | Passwordless sudo is **not** available (`sudo -n true` requires a password) | The documented pattern will not work as written on this host |

## Git, hooks and secrets

| Rule assumption | Observed | Impact |
|---|---|---|
| `gitleaks` available to the pre-commit hook | **Missing** | Secret scan cannot run; `bin/dsh check` covers the harness repo only |
| Global `core.hooksPath` chains to repo hooks | **Unset** | No global hook chain exists |
| Retention job installed | **Missing** | Nothing purges logs/trash automatically; `retention` must be run manually |
| `~/.omp/agent/*.md` locked | No such files (only SQLite databases) | Rule is a no-op on this host |

## DSH integration

| Rule assumption | Observed | Impact |
|---|---|---|
| Specialized tools include `xd://lsp` | DSH exposes `read`, `grep`, `glob`, `edit`, `bash`; no `xd://` LSP | The manual says "an LSP tool when the host provides one" |
| Global instructions are auto-loaded | `~/.agents/AGENTS.md` symlink is active | Loaded in new sessions |
| `RULES.md` is auto-loaded | It is **not**; only `AGENTS.md`/`CLAUDE.md` are discovered | `AGENTS.md` points to it; paste/read when delegating |
| Host commands are unrestricted | DSH file policy was widened to `danger-full-access` for this session | Provisioning succeeded; future sessions may differ |

## Risk review of the rules themselves

1. **`Write`/`Edit` over an existing file is gate-class.** In a clean Git repository the tracked-file exemption applies, but outside VCS almost every edit becomes a Five-Step Gate. This conflicts with "reversible work proceeds immediately". Recommendation: scope the clause to targets with no version history and no verified backup.
2. **`security … | sudo -S`** requires passwordless sudo (not available here) and cannot feed a command that reads stdin. Prefer DSH approval or a scoped `NOPASSWD` rule for named commands.
3. **`preflight` at every session** now works, but the 7 warnings are permanent until the host gaps above are closed; agents will repeat them once per session as the rule requires.
4. **Subagent rules are advisory.** Pasting rules 1–7 and requiring `AGENTS.md` §2 is the correct mechanism; compliance still needs review of their output.
5. **`bin/` locking is a speed bump, not security.** The owner can always unlock; it exists to make self-modification visible.

## Recommended order

1. Add `~/.ssh/config` host blocks, set `SSH_AUTH_SOCK`, and verify `newton`/`mediaserver` reachability from outside.
2. Install `gitleaks` and the chained global pre-commit hook.
3. Review and install the retention LaunchAgent; then let it own purges.
4. Decide the non-VCS edit-gate policy before applying the rules broadly.
5. Optional: `sudo ln -s /opt/agents /agents` and add `/opt/agents/bin` to `PATH`.
