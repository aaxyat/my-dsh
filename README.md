# my-dsh

Personal, portable source of truth for my [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (DSH) setup — instructions, profile configuration, skills, plugins, MCP servers and the tooling that reproduces them on a new Mac.

This repository is configuration, not application code. It answers one question: **what do I need to copy onto a fresh machine to get my harness back?**

---

## Principles

1. **The repo is the source of truth.** Live files under `~/.dsh` and `~/.agents` are deployment targets. If they differ, the repo wins — or the difference is captured deliberately.
2. **No secrets, ever.** `~/.dsh/.credentials.yaml`, API keys and session data never enter Git. See [docs/secrets.md](docs/secrets.md).
3. **Everything is declared.** Each deployed artifact is listed in [harness/manifest.json](harness/manifest.json) with its source, target and deploy mode.
4. **Reversible changes.** `apply` backs up what it replaces; every change is a reviewable Git diff.
5. **Boring and readable.** Plain Markdown and JSON, POSIX shell, stdlib Python. No runtime dependencies beyond what DSH already installs.

## Quick start (new machine)

```sh
# 1. Install the matching DSH desktop app, then:
git clone https://github.com/aaxyat/my-dsh.git ~/Documents/Projects/my-dsh
cd ~/Documents/Projects/my-dsh

# 2. Inspect, then deploy
./bin/dsh doctor
./bin/dsh apply --dry-run
./bin/dsh apply

# 3. Put credentials back in the keychain/credentials file (never in this repo)
# 4. Install optional personal plugins, then restart DSH
./bin/dsh apply --with-plugins
```

Full walkthrough: [docs/restore.md](docs/restore.md).

## Daily loop

```sh
# Changed a setting in the DSH app, installed a plugin, or edited a skill?
./bin/dsh capture        # pull live state into the repo + refresh inventory
git diff                 # review what actually changed
./bin/dsh check          # validate the repo (CI runs this too)
git add -A && git commit -m "chore(profile): ..." && git push
```

If you edit the repo first, run `./bin/dsh apply` to deploy, then `./bin/dsh doctor` to confirm.

## Commands

| Command | What it does |
|---|---|
| `./bin/dsh doctor` | Report repo, Git, DSH install, profile and symlink health. |
| `./bin/dsh check` | Validate the repo only: manifest, JSON/YAML, Markdown links, skills, secrets. Safe in CI. |
| `./bin/dsh capture` | Copy live profile files into `harness/`, refresh `machine/inventory.json`, and report drift. |
| `./bin/dsh apply` | Deploy the repo to this machine (backs up replaced files; refuses silent overwrites). |
| `./bin/dsh link` | Create only the symlinks (instructions + skills). Use after editing a skill. |
| `./bin/dsh apply --with-plugins` | Also install personal plugins declared `enabled: true` in the manifest. Requires a DSH restart. |
| `python3 tools/provision_agents.py` | Create/update `/opt/agents` (layout, helpers, lock). Idempotent; `--dry-run` first. |

`make check`, `make capture`, `make apply`, `make link`, `make doctor` are equivalent.

## Layout

```
AGENTS.md                  # rules for agents working in this repo (DSH loads it)
HANDOFF.md                 # living handoff: current state, decisions, next actions
README.md                  # this file
CHANGELOG.md               # human-readable history
bin/dsh                    # the only entry point you need
tools/dshctl.py            # implementation of capture/apply/link/check/doctor
tools/provision_agents.py  # installs agents/ into /opt/agents
agents/                    # durable agent workspace source (helpers, layout, README)
docs/                      # architecture, workflow, restore, secrets, ADRs, templates
harness/
  manifest.json            # declared artifacts (source -> target, mode)
  instructions/AGENTS.md   # global operating manual -> ~/.agents/AGENTS.md
  instructions/RULES.md    # compact rules 1-7 for subagents -> ~/.agents/RULES.md
  profile/desktop/         # cordis.patch.yml, package.json, pnpm-workspace.yaml
  skills/                  # personal skills -> ~/.agents/skills/<name>
  plugins/                 # personal bundles + registry of third-party bundles
  mcp/servers.yaml         # MCP server inventory (deployed via the profile patch)
  tools/README.md          # where "tools" come from in DSH
machine/inventory.json     # generated snapshot of the machine that produced this repo
```

## What is managed

| Surface | Where it lives here | Deploy mode |
|---|---|---|
| User-global agent rules | `harness/instructions/AGENTS.md` (manual) and `RULES.md` (compact rules for subagents) | symlinks to `~/.agents/` |
| Personal skills | `harness/skills/<name>/SKILL.md` | symlinked per skill into `~/.agents/skills/` |
| Profile patch (models, UI, settings) | `harness/profile/desktop/cordis.patch.yml` | copy |
| Profile bundle selection and deps | `harness/profile/desktop/package.json` | copy |
| Personal plugins | `harness/plugins/<name>/` | `pnpm link` on demand |
| Third-party plugins | recorded in `harness/plugins/registry.yaml` | reinstalled from registry |
| MCP servers | `harness/mcp/servers.yaml` + profile patch rows | part of the profile patch |
| Machine/Dsh versions | `machine/inventory.json` | generated snapshot |
| Agent workspace (`/opt/agents`) | `agents/` | provisioned by `tools/provision_agents.py` |

Not managed: DSH application binaries, sessions, runtime toolchains, credentials, caches. See [harness/manifest.json](harness/manifest.json) `excluded`.

## Status

Bootstrapped **2026-11-11** against DSH desktop **0.2.2-rc.1** on macOS (arm64), profile `desktop`.
The global agent rules (`AGENTS.md` + `RULES.md`) are deployed from this repo and load in new sessions. One personal plugin (`@local/pinned-workspaces`) is installed from `harness/plugins/`. `/opt/agents` is provisioned with 10 helpers and a locked `bin/`; `preflight` exits 0 with warnings for the still-missing SSH config, `gitleaks`, hook chain and retention job — see [docs/host-readiness.md](docs/host-readiness.md).

## Documentation

- [docs/architecture.md](docs/architecture.md) — how DSH loads configuration (verified against 0.2.2-rc.1)
- [docs/layout.md](docs/layout.md) — where every kind of file belongs
- [docs/workflow.md](docs/workflow.md) — change lifecycle, recipes, commit conventions
- [docs/restore.md](docs/restore.md) — rebuild on a new machine
- [docs/secrets.md](docs/secrets.md) — credential handling and incident response
- [docs/inventory.md](docs/inventory.md) — current captured state
- [docs/host-readiness.md](docs/host-readiness.md) — rule assumptions vs. this machine
- [docs/troubleshooting.md](docs/troubleshooting.md) — common failures
- [docs/decisions/](docs/decisions/) — architecture decision records
- [HANDOFF.md](HANDOFF.md) — what to do next

## License

Private configuration, published publicly for portability. No license is granted for reuse. See [HANDOFF.md](HANDOFF.md#open-questions) if you want a different default.
