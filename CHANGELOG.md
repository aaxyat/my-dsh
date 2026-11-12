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
- `harness/plugins/btw/`: personal Host + Web Client bundle implementing `/btw` read-only side questions — session-fork context, execution-time tool denial, in-flight parent snapshot, durable topic history, streaming/cancellation, and insert-into-composer. Built `lib/` is committed; provenance and Apache-2.0 notices are in the directory.
- The live `desktop` profile links and selects `@local/btw`; `harness/manifest.json`, `harness/plugins/registry.yaml`, and `machine/inventory.json` record it.
- `harness/plugins/parallel-mcp/`: configuration-only bundle mounting Parallel MCP anonymously as `mcp-parallel` (`web_search`, `web_fetch`, `web_decisions`, plus search utilities). No key or header is stored; `web_research` requires sign-in.
- The live `desktop` profile links and selects `@local/parallel-mcp`; `include:mcp-parallel` is active, and `harness/mcp/servers.yaml` records the server.
- `harness/plugins/playwright-mcp/`: configuration-only bundle for Playwright browser automation (`mcp__playwright__*`), plus `tools/provision_playwright_mcp.py` to install `@playwright/mcp` and Chromium under `/opt/agents/tools/playwright-mcp`. A live navigation to `example.com` succeeded.
- `harness/plugins/context7-mcp/`: configuration-only bundle for Context7 library documentation (`resolve-library-id`, `query-docs`) over the anonymous remote endpoint.
- `harness/plugins/cloudflare-mcp/`: configuration-only bundle for the Cloudflare documentation MCP server. The account API server (`mcp.cloudflare.com`) requires OAuth and is not mounted.
- The live `desktop` profile links and selects all three bundles; `include:mcp-playwright`, `include:mcp-context7` and `include:mcp-cloudflare` are active.
- Third-party `dsh-widgets@1.8.5` installed from npm and selected: a right-hand live widget rail with 61 session, machine, quota and cost cards. Recorded in `harness/plugins/registry.yaml`; not vendored. npm 1.8.5 is the latest published release.
- OpenViking memory: installed OpenViking `0.5.4.1` with local Ollama `qwen3-embedding:0.6b` and the free OpenCode Go `longcat-2.5-free` VLM with `deepseek-v4.1-flash` as the ordered fallback; the server is healthy at `127.0.0.1:1933`. Installed `@openviking/dsh-memory-plugin@0.5.34`; the runtime is active and exposes `mcp__openviking__*` plus the OpenViking skills. A sentinel write and search round-trip succeeded. OpenViking runs from a user LaunchAgent and Ollama from Homebrew services. The server config is `~/.openviking/ov.conf` (mode `0600`), not in this repository.
- Third-party `billion-context@0.1.213` installed from npm and selected: model-driven ACP context compression (`compress`, `decompress`, `search_context`, `acp_status`) for long single sessions. Its `bili-native` and `bili-compaction-gate` entries are active, and `acp_status` reports the running surface. The bundle disables DSH auto-compaction so ACP owns context policy. Recorded in `harness/plugins/registry.yaml`; not vendored.

### Added (agent workspace)

- `agents/`: tracked source for `/opt/agents` — layout README plus `preflight`, `manifest`, `rm`, `gate-rm`, `undo-rm`, `git-snapshot`, `ssh-probe`, `ssh-verify`, `sshd-apply`, `retention`.
- `tools/provision_agents.py`: idempotent installer with `--dry-run`, `--force`, `--no-lock`; records `state/provision.json` and locks `bin/` with `chflags`.
- `manifest.agentWorkspace` and inventory reporting for the installed workspace.
- `docs/host-readiness.md`: refreshed with provisioned status, smoke-test evidence and remaining SSH/hook/retention gaps.

### Fixed

- Removed all `/agents` alias references; the durable workspace is addressed only as `/opt/agents`.
- SSH auth uses Bitwarden via `~/.ssh/config` + `~/.zshenv`; `preflight` verifies the `IdentityAgent` instead of only `SSH_AUTH_SOCK`.
- `newton` and `mediaserver` are treated as Tailscale MagicDNS names (resolved, no `Host` blocks); added the 3-minute `ControlPersist` policy with `mediaserver` exempt and verified the effective settings with `ssh -G`.
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
