# Changelog

All notable changes to this harness repository are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows the date of a working configuration checkpoint.

## [Unreleased]

### Added

- Nothing yet.

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
