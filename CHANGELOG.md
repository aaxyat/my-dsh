# Changelog

All notable changes to this harness repository are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the date of a working configuration checkpoint.

## [Unreleased]

### Added

- `harness/plugins/pinned-workspaces/`: package documentation for the personal bundle (behaviour, files, install/disable, provenance).
- The live `desktop` profile now links `@local/pinned-workspaces` from this repository instead of the legacy pre-repo directory.
- Global operating rules: `harness/instructions/AGENTS.md` replaced with the user-supplied manual, plus `harness/instructions/RULES.md` (compact rules 1–7 for subagent prompts). Both deploy to `~/.agents/` as symlinks.
- `docs/host-readiness.md`: audit of the rules' `/opt/agents`, helper, SSH and hook assumptions against this machine.
- `machine/inventory.json` now records every instruction artifact, not just the first.

### Added (agent workspace)

- `agents/`: tracked source for `/opt/agents` — layout README plus `preflight`, `manifest`, `rm`, `gate-rm`, `undo-rm`, `git-snapshot`, `ssh-probe`, `ssh-verify`, `sshd-apply`, `retention`.
- `tools/provision_agents.py`: idempotent installer with `--dry-run`, `--force`, `--no-lock`; records `state/provision.json` and locks `bin/` with `chflags`.
- `manifest.agentWorkspace` and inventory reporting for the installed workspace.
- `docs/host-readiness.md`: refreshed with provisioned status, smoke-test evidence and remaining SSH/hook/retention gaps.

### Fixed

- `apply` warns when a copied profile references a personal plugin at a path that does not exist on the target machine.

## [0.1.0] - 2026-11-11

### Added

- Repository bootstrap: layout, manifest, governance and reference documentation.
- Captured the live `desktop` DSH profile (`cordis.patch.yml`, `package.json`, `pnpm-workspace.yaml`) from `~/.dsh/profiles/desktop`.
- Stored the personal `@local/pinned-workspaces` bundle under `harness/plugins/`; it is installed on the source machine via a `link:` dependency to its pre-repo path.
- `bin/dsh` CLI with `capture`, `apply`, `link`, `check` and `doctor` subcommands.
- User-global instruction draft at `harness/instructions/AGENTS.md`.
- Machine snapshot at `machine/inventory.json`.
- Documentation set: architecture, layout, workflow, restore, secrets, inventory, troubleshooting, ADRs and templates.
- GitHub Actions validation workflow.

### Security

- Credentials, sessions, caches and runtime toolchains are explicitly excluded from the repository; `.env` is ignored and only `.env.example` is tracked.
