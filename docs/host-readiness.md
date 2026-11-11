# Host readiness — global agent rules

Audit of the assumptions in [`harness/instructions/AGENTS.md`](../harness/instructions/AGENTS.md) and [`RULES.md`](../harness/instructions/RULES.md) against the current machine. Re-check this whenever a helper, host alias or global hook is added.

| | |
|---|---|
| Audited | 2026-11-11 |
| Host | Mac16,1 · arm64 · Darwin 27.0.0 |
| DSH | desktop `0.2.2-rc.1`, profile `desktop` |
| Verdict | **Rule files installed; supporting `/opt/agents` infrastructure is not provisioned.** Rules fall back to manual procedures, except where noted. |

## Infrastructure

| Rule assumption | Observed | Impact | Action |
|---|---|---|---|
| `/opt/agents` exists with `bin/data/state/logs/tmp` | Directory exists, owner `aaxyat`, mode `0755`, **empty** | No manifests, logs or state root; rules' layout is aspirational | Create the layout, or keep using `machine/` and repo-local scratch |
| `/opt/agents` is `0700` | `0755` | Looser than the rule requires | `chmod 700 /opt/agents` once its contents are reviewed |
| `/agents` symlink alias | Missing | Commands using `/agents` will fail | `ln -s /opt/agents /agents` (needs root) |
| `/opt/agents/README.md` | Missing | Provisioning reference in §7 is a dead pointer | Write it before relying on §7 |
| `/opt/agents/bin` is locked with `chflags uchg` | `bin/` does not exist; no flags set | Lock rule cannot be exercised | Provision, then lock deliberately |
| `~/.omp/agent/*.md` locked | No `*.md` files; only SQLite databases | Lock rule refers to files that do not exist on this host | Ignore until such files exist |

## Helpers

| Helper | State | Fallback |
|---|---|---|
| `preflight` | **missing** | Report `preflight: unavailable` once; use manual checks |
| `manifest`, `gate-rm`, `undo-rm`, `rm` shim | **missing** | Enumerate/hash manually; deletions are gate-class via the table |
| `git-snapshot` | **missing** | Use a branch/tag or `git stash create` + `git update-ref`, or gate the action |
| `ssh-probe`, `ssh-verify`, `sshd-apply` | **missing** | Run the individual commands in `AGENTS.md` §4 by hand |
| `retention` + LaunchAgent | **missing** | No retention runs; agents must not purge |
| `gitleaks` | **missing** | The pre-commit scan cannot run; `bin/dsh check` scans this repo instead |

`/opt/agents` being empty also means the rule "if `/opt/agents` is missing, hand the user the provisioning block and wait" does not trigger — the directory exists, so work proceeds with manual fallbacks.

## Remote hosts

| Rule assumption | Observed | Impact |
|---|---|---|
| `~/.ssh/config` defines `newton` and `mediaserver` | **No `~/.ssh/config`**; only `known_hosts` and an `agent/` directory | Host aliases and `ControlPersist` rules are not configured; SSH will only work if the names resolve and keys are accepted another way |
| Bitwarden SSH agent is the auth path | Socket `~/.bitwarden-ssh-agent.sock` exists | Auth may work if `SSH_AUTH_SOCK` points at it; no on-disk keys were found |
| `ControlPersist 3m`, off for `mediaserver` | Not configured | The approval-bypass risk described in §4 is not currently present |
| Keychain item `newton-sudo` is an unattended fallback | Not verified | Unknown; do not rely on it |
| `sudo -S` can pipe a Keychain secret | Passwordless sudo not verified | The documented pattern may prompt or fail; DSH also sandboxes/approves host commands |

## DSH integration

| Rule assumption | Observed | Impact |
|---|---|---|
| Specialized tools include `xd://lsp` | DSH exposes `read`, `grep`, `glob`, `edit`, `bash`, and no `xd://lsp` | The rule was adapted to "an LSP tool when the host provides one"; never depend on `xd://` here |
| Global instructions are auto-loaded | `~/.agents/AGENTS.md` is now a symlink to this repo | Active for new sessions; the current session may retain the previous baseline |
| `RULES.md` is auto-loaded | It is **not**; only `AGENTS.md`/`CLAUDE.md` are discovered | `AGENTS.md` points to `~/.agents/RULES.md`; agents must read it when composing subagent prompts |
| Edits outside the workspace are free | DSH file policy is `workspace-write`; `~/.agents` and `/opt/agents` need approval/full access | Provisioning steps will prompt; deployment of these symlinks required wider access |

## Risk review of the rules themselves

1. **`Write`/`Edit` over an existing file is gate-class.** In a clean Git repository the tracked-file exemption applies, but outside VCS (scratch docs, `/opt/agents/data`, configs in `~/`) almost every edit becomes a Five-Step Gate. This conflicts with "reversible work proceeds immediately". Recommendation: scope the clause to targets with no version history and no verified backup.
2. **`security … | sudo -S`** pipes a secret into `sudo`; it works only with passwordless sudo, hides the prompt, and cannot feed a command that reads stdin. Prefer `sudo` approval via DSH, or a scoped `NOPASSWD` rule for named commands.
3. **`preflight` at every session** has no implementation here; the adapted rule degrades to a one-line "unavailable" notice, which keeps sessions unblocked but removes the safety net the rule assumes.
4. **Subagent rules are advisory.** DSH subagents receive a prompt, not an enforcement layer; pasting rules 1–7 and requiring `AGENTS.md` §2 is the correct mechanism, but compliance still needs review of their output.

## Recommended order

1. Provision `/opt/agents` (layout, README, helpers), then `chmod 700`.
2. Add `~/.ssh/config` host blocks and `SSH_AUTH_SOCK`; verify `newton`/`mediaserver` reachability from outside.
3. Install `gitleaks` and the chained global pre-commit hook.
4. Add the retention LaunchAgent if soft-delete is adopted.
5. Decide the non-VCS edit-gate policy before applying the rules broadly.
