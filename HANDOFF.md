# HANDOFF

Living handoff for this repository. **Read this first, update it last.**

It answers: where the setup stands, what was decided, what is still open, and what the next person (or agent) should do. It is not a changelog — history lives in [`CHANGELOG.md`](CHANGELOG.md) and Git.

---

## Snapshot

| Field | Value |
|---|---|
| Status | Bootstrapped, provisioned, validated, published |
| As of | 2026-11-11 |
| Repository | https://github.com/aaxyat/my-dsh (public) |
| DSH desktop | `0.2.2-rc.1` (darwin / arm64) |
| Profile | `desktop` |
| DSH home | `~/.dsh` |
| Shared agents home | `~/.agents` (created by `bin/dsh link`) |
| Personal skills | 0 (scaffolding ready) |
| Personal plugins | 1 installed (`@local/pinned-workspaces`, linked from `harness/plugins/`) |
| Third-party plugins | 0 |
| MCP servers | 0 |
| Managed artifacts | 6 + 1 personal plugin |
| Global rules | `AGENTS.md` + `RULES.md` deployed as symlinks |
| Agent workspace | `/opt/agents` provisioned from `agents/` · 10 helpers · `bin/` locked |

Verified on the originating machine:

- `./bin/dsh check` — repository validation.
- `./bin/dsh doctor` — environment and symlink health.
- `./bin/dsh apply --dry-run` — no unexpected conflicts.
- Profile files copied byte-for-byte from `~/.dsh/profiles/desktop/`.
- `@local/pinned-workspaces` relinked from this repository; `pnpm add link:` succeeded and `capture` recorded the new dependency path.
- `/opt/agents` provisioned and `preflight` exits 0 with 7 warnings (SSH config, `gitleaks`, hooks, retention, PATH, alias).
- Helper smoke tests: manifest, soft delete + undo, git snapshot (temp repo, index untouched), retention dry/apply, sshd-apply refusal, protected-path refusal.

## What exists

```
AGENTS.md                 repo rules (loaded by DSH as workspace instructions)
HANDOFF.md                this file
README.md                 orientation and command reference
CHANGELOG.md              release history
bin/dsh                   CLI entry point
tools/dshctl.py           capture / apply / link / check / doctor
docs/                     architecture, layout, workflow, restore, secrets, inventory, troubleshooting, ADRs, templates
harness/manifest.json     every deployed artifact: source, target, mode
harness/instructions/     user-global AGENTS.md
harness/profile/desktop/  profile patch, package.json, pnpm-workspace.yaml
harness/skills/           personal skills (empty, documented)
harness/plugins/          personal bundles + third-party registry
harness/mcp/              MCP inventory
harness/tools/            where "tools" come from in DSH
machine/inventory.json    generated snapshot of the captured machine
```

## Decisions made during bootstrap

| # | Decision | Rationale |
|---|---|---|
| 1 | Repo is the source of truth; live paths are deployment targets | Makes a new machine reproducible and every change reviewable. |
| 2 | Instructions and skills are **symlinked**, profile files are **copied** | Read-only artifacts benefit from live editing in Git; profile files are written by DSH/pnpm, so copying + capture avoids atomic-write clobbering symlinks. |
| 3 | Machine-readable manifest is JSON, app-facing config stays YAML | Scripts need zero YAML dependencies; DSH-native files keep their format. |
| 4 | Credentials excluded; config references env names only | Public repository. |
| 5 | `apply` refuses to overwrite differing live files without `--force` | Prevents silently destroying changes made in the app. |
| 6 | Third-party plugins are recorded, not vendored | Keeps the repo small and respects upstream licenses/updates. |
| 7 | Global instructions deploy to `~/.agents/AGENTS.md`, not `~/.dsh/AGENTS.md` | Tool-agnostic location; DSH deduplicates identical content if both exist. |
| 8 | `/opt/agents` is provisioned from the tracked `agents/` tree | Helpers become reviewable, versioned and reproducible; the installer owns layout, hashes and the `chflags` lock. |

Full rationale: [`docs/decisions/`](docs/decisions/).

## Open questions

1. **License.** The public repo currently grants no reuse rights. Decide: keep unlicensed, add MIT, or make the repo private. Recorded as an open question because it is a user preference.
2. **Legacy `pinned-workspaces` directory.** The live profile now links the repo copy, but the original directory at `~/Documents/Projects/Deepseek/pinned-workspaces` still exists as an identical duplicate. Decide when to archive or delete it. Do not edit that copy going forward; this repository is canonical.
3. **Global rules content and adaptations.** The user-supplied manual is installed as `AGENTS.md`; `RULES.md` is the compact rules 1–7 derived from it. Three adaptations were made: `xd://lsp` is described as host-dependent, `preflight` absence degrades to a notice, and the companion path is explicit. Review those. The workspace itself is provisioned; remaining host gaps are listed in [docs/host-readiness.md](docs/host-readiness.md).
4. **Provider posture.** The profile's `llm-pi-ai` provider (`opencode-go`) fronts many third-party models through one endpoint and one key (`OPENCODE_GO_API_KEY`). This is captured as configuration only. If the endpoint or key handling changes, update the profile here — never commit the key.
5. **Capture cadence.** Today capture is manual. If drift becomes common, revisit a launchd/Git-hook automation (see ADR-0002 consequences).

## Next actions

Priority order:

1. **Restart DSH**, open a new session, and confirm the new global rules load (`AGENTS.md`), with `RULES.md` present at `~/.agents/`.
2. Close the remaining host gaps in [docs/host-readiness.md](docs/host-readiness.md): `~/.ssh/config` hosts + `SSH_AUTH_SOCK`, `gitleaks` + global hook chain, retention LaunchAgent, `PATH`, optional `/agents` alias.
3. Resolve the license question (README + `LICENSE`).
4. Add the first real personal skill under `harness/skills/<name>/` using [`docs/templates/SKILL.md`](docs/templates/SKILL.md), then `./bin/dsh link`.
5. When an MCP server is adopted, add its row to the profile patch and `harness/mcp/servers.yaml` in the same commit.
6. Re-run `./bin/dsh capture` after any change made in the DSH app, and commit.
7. Update `agents/bin/*` in the repo, then `python3 tools/provision_agents.py --force`; never edit `/opt/agents/bin` in place.

## Known gaps

- `/opt/agents` is provisioned and locked, but `PATH` is not wired, the `/agents` alias is absent (no passwordless sudo), and the retention LaunchAgent is not installed (human-owned). `preflight` reports 7 warnings.
- Remote-host helpers exist but were not exercised against a host: there is no `~/.ssh/config`, `SSH_AUTH_SOCK` does not point at Bitwarden, and `gitleaks`/global hooks are missing. `sshd-apply` intentionally refuses to mutate.
- Helper tests covered normal and guard paths, not large trees, cross-volume moves, or concurrent runs.
- `RULES.md` is not auto-loaded by DSH; it is a companion for composing subagent prompts and must be pasted or read explicitly.
- No personal skills or MCP servers exist yet, so those paths are exercised by docs/checks, not real content.
- The personal plugin's `link:` dependency is an absolute path; it is machine-specific even though it now points inside this repo. On a target machine, `apply --with-plugins` rewrites it.
- The legacy pre-repo plugin directory is an identical duplicate (open question 2). Only the repo copy should be edited.
- `apply --with-plugins` could not drive pnpm inside this session's file sandbox (pnpm's store lives outside the workspace). The equivalent `pnpm add link:` command succeeded manually with full access; the script's wrapper logic is still unproven end-to-end on a fresh machine.
- `check` warns rather than fails on machine-specific `link:` dependencies, uncaptured profile edits and missing inventory entries.
- Inventory is a point-in-time snapshot; it is not a live monitor.
- Windows/PowerShell is out of scope for now; scripts assume POSIX.

## Session log

Add one row per working session, newest first. Keep it terse; details belong in commits.

| Date | Session | Outcome |
|---|---|---|
| 2026-11-11 | Bootstrap | Repo initialized; DSH config inventoried; profile, personal plugin and instructions captured; CLI (`capture/apply/link/check/doctor`), docs, ADRs, manifest, CI added; validated and pushed to GitHub. |
| 2026-11-11 | Plugin tracking | Documented `@local/pinned-workspaces`; repointed the live `desktop` profile link from the pre-repo directory to `harness/plugins/pinned-workspaces/`; captured the new dependency and inventory. |
| 2026-11-11 | Global rules | Installed the user-supplied operating manual as the auto-loaded `AGENTS.md`; added the derived compact `RULES.md`; deployed both to `~/.agents/`; audited rule assumptions in `docs/host-readiness.md`. |
| 2026-11-11 | Agent workspace | Added the tracked `agents/` tree and idempotent `tools/provision_agents.py`; provisioned `/opt/agents` with 10 helpers, `0700` layout and a locked `bin/`; smoke-tested the helpers and recorded the results in `docs/host-readiness.md`. |

---

## How to update this file

At the end of any session that changes the repository:

1. Update **Snapshot** (date, counts, status).
2. Add/remove **Open questions** and **Next actions** — this file must always tell the next agent what to do.
3. Add one **Session log** row.
4. Move completed next actions out; do not leave stale TODOs.
5. Keep it under ~150 lines. If it grows, split reference detail into `docs/` and link it.
