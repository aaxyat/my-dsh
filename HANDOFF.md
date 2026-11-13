# HANDOFF

Living handoff for this repository. **Read this first, update it last.**

It answers: where the setup stands, what was decided, what is still open, and what the next person (or agent) should do. It is not a changelog — history lives in [`CHANGELOG.md`](CHANGELOG.md) and Git.

---

## Snapshot

| Field | Value |
|---|---|
| Status | Bootstrapped, provisioned, validated, published |
| As of | 2026-11-13 |
| Repository | https://github.com/aaxyat/my-dsh (public) |
| DSH desktop | `0.2.2-rc.1` (darwin / arm64) |
| Profile | `desktop` |
| DSH home | `~/.dsh` |
| Shared agents home | `~/.agents` (created by `bin/dsh link`) |
| Personal skills | 0 (scaffolding ready) |
| Third-party skills | 44 from 3 pinned packs — `mattpocock` (20, MIT), `anthropic` (7, Apache-2.0), `cursor` (17, MIT); `obra/superpowers` deliberately skipped because it would shadow Aegis |
| Personal plugins | 6 installed (`@local/pinned-workspaces`, `@local/btw`, and the `parallel-mcp`, `playwright-mcp`, `context7-mcp`, `cloudflare-mcp` configuration bundles, linked from `harness/plugins/`) |
| Third-party plugins | 5 (`dsh-widgets` 1.8.5, `@openviking/dsh-memory-plugin` 0.5.34 and `billion-context` 0.1.213 from npm; `aegis` 2.15.0 from a GitHub tag; `dshmarket` 1.73.17 from npm) |
| MCP servers | 4 configured (`parallel-mcp`, `playwright`, `context7`, `cloudflare`) plus the `openviking` MCP tools from the memory plugin; `cloudflare` reaches the full API through an `mcp-remote` stdio bridge |
| Managed artifacts | 7 + 6 personal bundles |
| Replication runbook | [`SETUP.md`](SETUP.md) — one file, eight commands, no repository exploration |
| Global rules | `AGENTS.md` + `RULES.md` deployed as symlinks |
| Agent workspace | `/opt/agents` provisioned from `agents/` · 10 helpers · `bin/` locked |
| SSH auth | Bitwarden `IdentityAgent`; `newton` verified; `mediaserver` host key pending |

Verified on the originating machine:

- `./bin/dsh check` — repository validation.
- `./bin/dsh doctor` — environment and symlink health.
- `./bin/dsh apply --dry-run` — no unexpected conflicts.
- Profile files copied byte-for-byte from `~/.dsh/profiles/desktop/`.
- `@local/pinned-workspaces` relinked from this repository; `pnpm add link:` succeeded and `capture` recorded the new dependency path.
- `@local/btw` built from `harness/plugins/btw/src`, linked into the `desktop` profile and selected; the running Web server serves its client bundle (the `/plugins/??@local/btw/client.js&rev=…` combo route returned 200 with the rebuilt module), and `plugin-manager` reports `include:btw` as `active`.
- `/btw` bundle checks: `tsc --noEmit` against DSH `0.2.2-rc.1` types, 58/58 Vitest tests, esbuild build, and built-artifact smoke (Host export, Client loader id `@local/btw`, `/btw` claim without `crypto.randomUUID`).
- `@local/parallel-mcp` configuration-only bundle installed and selected; `plugin-manager` reports `include:mcp-parallel` as `active`, and the tool catalog includes `mcp__parallel-mcp__web_search`, `web_fetch`, `web_decisions`, plus the search utilities.
- Live Parallel check: one anonymous `web_search` for today's tech headline returned dated results; no `web_research` (sign-in required).
- `@local/playwright-mcp`, `@local/context7-mcp` and `@local/cloudflare-mcp` configuration-only bundles installed and selected; `include:mcp-playwright`, `include:mcp-context7` and `include:mcp-cloudflare` are all `active`.
- Playwright check: `tools/provision_playwright_mcp.py` installed `@playwright/mcp@0.0.85` and Chromium under `/opt/agents/tools/playwright-mcp`; `browser_navigate` loaded `https://example.com` and returned `Example Domain`, then closed cleanly.
- Context7 check: `resolve-library-id` for React returned `/reactjs/react.dev` and four other candidates.
- Cloudflare check: `tools/provision_cloudflare_mcp_oauth.py` installed `mcp-remote@0.16.6` under `/opt/agents/tools/cloudflare-mcp-oauth` with install scripts disabled; a one-time browser OAuth grant (`user:read account:read offline_access`) cached tokens in `~/.mcp-auth` (mode `0600`), and a stdio handshake through the bridge returned server `cloudflare-api` 0.1.0 with tools `docs`, `search`, `execute`, `whoami`. This replaced the anonymous documentation server.
- `dsh-widgets@1.8.5` installed from npm and selected; `plugin-manager` reports `include:widgets` as `active`. npm 1.8.5 is the latest published version (GitHub `main` is 1.9.0, unreleased). UI placement was not visually exercised.
- OpenViking `0.5.4.1` installed with `uv` under Python 3.13; doctor passes, `/health` and `/ready` are 200 on `http://127.0.0.1:1933`. Embeddings use local Ollama `qwen3-embedding:0.6b` (1024 dims); the VLM is the free OpenCode Go `longcat-2.5-free` with `deepseek-v4.1-flash` as the ordered fallback; both use the OpenAI-compatible endpoint with `thinking: false` and the required `x-opencode-session` header.
- `@openviking/dsh-memory-plugin@0.5.34` installed and selected; `include:openviking-memory-runtime` is `active`, `mcp__openviking__*` tools are in the catalog, and the four OpenViking skills appear.
- Failover test: a temporary primary of `deepseek-v4.1-flash-free` returned 429 twice, the log reported `Credential zen-free-primary failed with rate_limit_error, trying next credential`, and the fallback completed the memory extraction.
- End-to-end memory test: `remember` submitted a sentinel, `SessionCommit` processed it, and `search` returned `viking://user/default/memories/events/2026/11/12/openviking_pipeline_verified.md`; the VLM also answered a direct image prompt (`Teal`).
- `billion-context` 0.1.213 installed and active: `include:bili-native` and `include:bili-compaction-gate` are `active`; the tool catalog exposes `compress`, `decompress`, `search_context` and `acp_status`. `acp_status` reports `ACTIVE SURFACE: host=billion-context 0.1.213`. A live round-trip compressed 553 messages (140.0K→1.3K) plus 12 messages (1.9K→430) into blocks `b1` and `b2`; `acp_status` reports 2 active blocks, 141.9K original and a 1.0× billed/estimate ratio.
- `aegis` 2.15.0 installed natively through the Desktop plugin manager from `github:GanyuanRan/Aegis#v2.15.0`; `include:aegis-method-pack` is `active`, the profile lists `aegis` in both dependencies and `dsh.profile.bundles`, and the method pack contributes 23 skills. CLI `dsh plugin --profile desktop` is not a usable path because the Electron app owns that profile.
- Aegis doctor run from `/Users/aaxyat/.dsh/profiles/desktop/node_modules/aegis`: `python3 scripts/aegis-doctor.py --write-config --json` returned `"ok": true`, `"workspaceSupport": "available"`, `"configStatus": "configured"`; all 14 checks passed. `python` is not installed, so `python3` 3.15.2 was used.
- Aegis automatic entry verified in a fresh Desktop session (`session-0b67f5a9-98cf-4529-aefa-87f1adfcfca9`): `AEGIS_DSH_ROUTING_BOOTSTRAP` appears in `agent/inbox/spliced` and again in `user/message` after the first tool calls, and the agent loaded `systematic-debugging` through the native `skill` tool and completed the turn.
- `dshmarket` 1.73.17 installed into the `web` profile with `dsh plugin --profile web add dshmarket` (using the bundled Node/pnpm through a temporary shim) and into the `desktop` profile with the app plugin manager. `include:dsh-market` is `active` in Desktop (`moduleName: dshmarket`); the web profile records the dependency and bundle patch. The web UI was not booted: the temporary CLI failed with `No usable native binding found for node-addon-require-builtin-darwin-arm64`, so the market page is not visually verified.
- Third-party skill packs installed without vendoring: `harness/skills/packs.json` pins three packs, `./bin/dsh skills sync` cloned them at the pinned commits into `/opt/agents/tools/skill-packs/` and linked 44 skills into `~/.agents/skills`. The live session catalog gained all 34 model-invocable skills, and the native `skill` tool loaded `deslop` from the pack clone. Re-sync is idempotent (`0 link(s) changed`), `--offline` works from the existing clones, prune removed a deselected link and relinked it when restored, and a real directory at a skill name was refused with `nothing was overwritten`.
- `/opt/agents` provisioned and `preflight` exits 0 with 5 warnings (mediaserver host key, `gitleaks`, hooks, retention, PATH).
- Bitwarden SSH agent verified end-to-end: `ssh-verify newton` succeeded; `newton` multiplexes for 180 s and `mediaserver` is exempt.
- Tailnet names resolve directly: `newton` → `100.94.136.32`, `mediaserver` → `100.74.97.34`; no `Host` blocks needed.
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
| 9 | `/btw` is a vendored Apache-2.0 personal bundle, not a registry-only third-party install | We must rename it, build against the installed DSH and fix it without waiting for upstream; see [ADR-0005](docs/decisions/0005-btw-plugin-fork.md). |

Full rationale: [`docs/decisions/`](docs/decisions/).

## Open questions

1. **License.** The public repo currently grants no reuse rights. Decide: keep unlicensed, add MIT, or make the repo private. Recorded as an open question because it is a user preference.
2. **Legacy `pinned-workspaces` directory.** The live profile now links the repo copy, but the original directory at `~/Documents/Projects/Deepseek/pinned-workspaces` still exists as an identical duplicate. Decide when to archive or delete it. Do not edit that copy going forward; this repository is canonical.
3. **Global rules content and adaptations.** The user-supplied manual is installed as `AGENTS.md`; `RULES.md` is the compact rules 1–7 derived from it. Three adaptations were made: `xd://lsp` is described as host-dependent, `preflight` absence degrades to a notice, and the companion path is explicit. Review those. The workspace itself is provisioned; remaining host gaps are listed in [docs/host-readiness.md](docs/host-readiness.md).
4. **Provider posture.** The profile's `llm-pi-ai` provider (`opencode-go`) fronts many third-party models through one endpoint and one key (`OPENCODE_GO_API_KEY`). This is captured as configuration only. If the endpoint or key handling changes, update the profile here — never commit the key.
5. **Capture cadence.** Today capture is manual. If drift becomes common, revisit a launchd/Git-hook automation (see ADR-0002 consequences).
6. **License scope for `harness/plugins/btw/`.** The bundle carries its own Apache-2.0 LICENSE because it is derived from `dsh-btw-marginalia`, while the repository root still has no license. Decide whether to add a root LICENSE that covers the rest of the repo or keep per-directory licensing.

7. **User-invocable-only pack skills.** Ten selected skills declare `disable-model-invocation: true` upstream, so DSH hides them from the model catalog; they only run when invoked by name. Decide whether that is acceptable for `implement`, `to-spec`, `to-tickets`, `handoff` and friends, or whether one should be copied into `harness/skills/` with the flag removed.

## Next actions

Priority order:

1. **Restart DSH**, open a new session, and confirm the new global rules load (`AGENTS.md`), with `RULES.md` present at `~/.agents/`. Then run `/btw` with a question and confirm a bubble streams, Stop keeps the partial, and main transcript has no new rows. The same restart loads the rerouted `cloudflare` row — confirm `mcp__cloudflare__whoami` returns the authenticated account.
2. **Prove [`SETUP.md`](SETUP.md) on a clean target** — a fresh macOS account, VM or container — following it verbatim, and fix every step that needed an undocumented workaround. A step that cannot be completed without opening another file is a bug in the runbook.
3. Confirm the `mediaserver` host-key fingerprint out of band, then run `ssh-verify mediaserver`; install `gitleaks` + global hook chain, retention LaunchAgent, and wire `PATH`.
4. Resolve the license question (README + `LICENSE`).
5. Add the first real personal skill under `harness/skills/<name>/` using [`docs/templates/SKILL.md`](docs/templates/SKILL.md), then `./bin/dsh link`.
6. Parallel MCP is anonymous. To enable `web_research` and higher limits, change the bundle URL to `https://mcp.parallel.ai/mcp?login`, reinstall it, and complete the browser sign-in.
7. Re-run `./bin/dsh capture` after any change made in the DSH app, and commit.
8. Update `agents/bin/*` in the repo, then `python3 tools/provision_agents.py --force`; never edit `/opt/agents/bin` in place.
9. Boot a Web runtime with a working native binding, open Settings → dshmarket, and confirm the market page and one-click install; then decide whether to pin or upgrade from 1.73.17 to 1.73.19.

## Known gaps

- `/opt/agents` is provisioned and locked, but `PATH` is not wired and the retention LaunchAgent is not installed (human-owned). `preflight` reports 5 warnings.
- `newton` works end-to-end through Bitwarden. `mediaserver` is reachable but its host key is untrusted (`SHA256:RglUseR9rW45O8xzdqCJt/+p9McsC7E3r81lwnNdabE`), so authentication was not exercised; `gitleaks`/global hooks are still missing. `sshd-apply` intentionally refuses to mutate.
- Helper tests covered normal and guard paths, not large trees, cross-volume moves, or concurrent runs.
- `RULES.md` is not auto-loaded by DSH; it is a companion for composing subagent prompts and must be pasted or read explicitly.
- No personal skills exist yet; four MCP servers are configured and all four were exercised with live calls. The OpenViking plugin adds `mcp__openviking__*` tools on top. Parallel `web_research` needs sign-in; Cloudflare reaches the full API through the `mcp-remote` bridge because DSH's MCP client has no OAuth flow; Context7 runs anonymously at lower limits.
- The personal plugin's `link:` dependency is an absolute path; it is machine-specific even though it now points inside this repo. On a target machine, `apply --with-plugins` rewrites it.
- The Playwright row hardcodes the DSH runtime Node path and `/opt/agents/tools/playwright-mcp`; its Chromium download is ~584 MB. `tools/provision_playwright_mcp.py` recreates the tool but does not rewrite the row.
- The Cloudflare row hardcodes the same Node path plus `/opt/agents/tools/cloudflare-mcp-oauth`, and its OAuth tokens live in `~/.mcp-auth` (outside this repository and outside `/opt/agents`, by design). A revoked or expired refresh token makes the row fail at startup until the login command in the bundle README is re-run. `tools/provision_cloudflare_mcp_oauth.py` recreates the bridge but does not rewrite the row.
- `@local/btw` was installed and selected while the current DSH process was already running. The server serves its client bundle and the bundle's unit/smoke checks pass, but the slash menu, bubble streaming, Stop/partial retention and read-only denial were not exercised through a live GUI turn; that needs the restart in Next action 1.
- The legacy pre-repo plugin directory is an identical duplicate (open question 2). Only the repo copy should be edited.
- `apply --with-plugins` could not drive pnpm inside this session's file sandbox (pnpm's store lives outside the workspace). The equivalent `pnpm add link:` command succeeded manually with full access; the script's wrapper logic is still unproven end-to-end on a fresh machine.
- `check` warns rather than fails on machine-specific `link:` dependencies, uncaptured profile edits and missing inventory entries. It also warns that the four `*-mcp` bundles have no `dsh.client.platform`; that is expected because they are configuration-only and ship no Client half.
- OpenViking starts at login through `~/Library/LaunchAgents/sh.omp.openviking-server.plist` (`KeepAlive`, logs under `/opt/agents/logs/`); Ollama starts through Homebrew's `sh.brew.ollama` service. `~/.openviking/ov.conf` (mode `0600`) holds the OpenCode Go key outside this repository; rotating the DSH key requires updating it.
- OpenViking write/search works end to end; a later turn did receive an `<openviking-context>` recall block, so pre-step recall is working.
- `billion-context` disables DSH auto-compaction by design and hands context policy to ACP; its Web `/compact` behavior and interaction with the OpenViking recall path were not exercised. The current session surface already had ACP tools before the profile bundle was added, so the bundle may be attaching to an existing proxy rather than spawning a second one.
- `aegis` is installed from a Git tag and is not vendored; updating it requires the Desktop plugin manager because the Electron app owns the `desktop` profile. `python` is absent, so the doctor must be run with `python3`. The fresh-session smoke test covered bootstrap injection and skill discovery, not routing quality across real tasks.
- `dshmarket` is installed in both `web` and `desktop`, but only the Desktop row is verified active. The web profile was initialized and the package installed; `dsh web` could not boot because the temporary CLI lacked a Node ABI 137 native binding, so the market UI and its one-click installs are unverified. npm latest is 1.73.19; the install resolved 1.73.17.
- OpenCode Zen's free text/vision models returned `FreeUsageLimitError` (429) for this key, and `jev-1.13-free` is a structured-decision endpoint, not a text/vision model. OpenViking therefore uses the Go-included free `longcat-2.5-free`; embeddings remain local.
- Windows/PowerShell is out of scope for now; scripts assume POSIX.

## Session log

Add one row per working session, newest first. Keep it terse; details belong in commits.

| Date | Session | Outcome |
|---|---|---|
| 2026-11-13 | Third-party skills | Installed 44 general-purpose skills from `mattpocock`, `anthropics/skills` and `cursor/plugins` without vendoring: `harness/skills/packs.json` records repo + pinned commit + selection + exclusion reasons, a new `packs` manifest mode and `skills sync|status` subcommands clone into `/opt/agents/tools/skill-packs/` and link into `~/.agents/skills`. `superpowers` skipped (13/15 names would shadow Aegis). Discovery verified live via the `skill` tool; prune, conflict refusal and offline paths exercised. |
| 2026-11-11 | Bootstrap | Repo initialized; DSH config inventoried; profile, personal plugin and instructions captured; CLI (`capture/apply/link/check/doctor`), docs, ADRs, manifest, CI added; validated and pushed to GitHub. |
| 2026-11-11 | Plugin tracking | Documented `@local/pinned-workspaces`; repointed the live `desktop` profile link from the pre-repo directory to `harness/plugins/pinned-workspaces/`; captured the new dependency and inventory. |
| 2026-11-11 | Global rules | Installed the user-supplied operating manual as the auto-loaded `AGENTS.md`; added the derived compact `RULES.md`; deployed both to `~/.agents/`; audited rule assumptions in `docs/host-readiness.md`. |
| 2026-11-11 | Agent workspace | Added the tracked `agents/` tree and idempotent `tools/provision_agents.py`; provisioned `/opt/agents` with 10 helpers, `0700` layout and a locked `bin/`; smoke-tested the helpers and recorded the results in `docs/host-readiness.md`. |
| 2026-11-11 | Cleanup | Removed every `/agents` alias reference; the workspace is addressed only by `/opt/agents`. Fixed SSH auth with Bitwarden `IdentityAgent`, `~/.zshenv` and `launchctl`; recognized `newton`/`mediaserver` as MagicDNS names, added the `ControlPersist` policy, and verified `newton`. `preflight` reports 5 warnings. |
| 2026-11-11 | `/btw` plugin | Added `harness/plugins/btw/`: a Host + Web Client bundle (derived from Apache-2.0 `dsh-btw-marginalia`) for read-only `/btw` side questions, with committed `lib/`. Typechecked against 0.2.2-rc.1, 58/58 tests, build + smoke pass; linked and selected in the `desktop` profile, and the live Web server serves the client bundle. Live GUI turn still needs the restart. |
| 2026-11-11 | Parallel search | Added the `@local/parallel-mcp` configuration-only bundle, linked and selected in the `desktop` profile; `mcp-parallel` is active and exposes `web_search`, `web_fetch`, `web_decisions` and search utilities. Anonymous mode; a live search succeeded, `web_research` needs sign-in. |
| 2026-11-11 | More MCP servers | Added `playwright-mcp`, `context7-mcp` and `cloudflare-mcp` configuration bundles, all active. Provisioned Playwright MCP and Chromium under `/opt/agents/tools/playwright-mcp` with `tools/provision_playwright_mcp.py`; verified a real Playwright navigation, a Context7 library lookup and a Cloudflare docs search. |
| 2026-11-12 | Widgets | Installed third-party `dsh-widgets@1.8.5` from npm; `include:widgets` is active and the profile selects it. npm 1.8.5 is the latest published release; GitHub main is 1.9.0. UI placement remains visually unverified. |
| 2026-11-12 | OpenViking | Installed OpenViking `0.5.4.1` and Ollama; configured local `qwen3-embedding:0.6b` plus the free OpenCode Go `longcat-2.5-free` for the VLM with `deepseek-v4.1-flash` as fallback; server is healthy on 127.0.0.1:1933. Installed `@openviking/dsh-memory-plugin@0.5.34`; the runtime is active, `mcp__openviking__*` tools and the four OpenViking skills are present. A sentinel write/search round-trip succeeded. OpenViking now runs from a user LaunchAgent; Ollama runs from Homebrew services. |
| 2026-11-12 | Context compression | Installed `billion-context` 0.1.213 into `desktop`; `bili-native` and `bili-compaction-gate` are active, the four ACP tools are in the catalog, and `acp_status` reports the surface. This is the DSH-native compression lane; Magic Context remains unsupported on DSH 0.2.2. |
| 2026-11-12 | Aegis | Installed `aegis` 2.15.0 natively through the Desktop plugin manager from GitHub tag `v2.15.0`; `include:aegis-method-pack` is active and the profile records the dependency. Doctor returned ok/available/configured. A fresh Desktop session received the deferred `AEGIS_DSH_ROUTING_BOOTSTRAP` after its first tool calls and loaded `systematic-debugging`. |
| 2026-11-12 | dshmarket | Installed `dshmarket` 1.73.17 into `web` via the CLI and into `desktop` via the app plugin manager; `include:dsh-market` is active in Desktop and the web profile records the dependency. Web UI boot failed on a missing native binding, so the market page remains unverified. |
| 2026-11-13 | Cloudflare MCP OAuth | Confirmed DSH `0.2.2-rc.2` has no MCP OAuth support (client config, package scans, manager's "No OAuth flow" limitation). Audited `mcp-remote@0.16.6` — integrity hash, no install scripts in the 221-entry dependency tree, loopback-only callback, no telemetry, `~/.mcp-auth` at `0600` — then installed it under `/opt/agents/tools/cloudflare-mcp-oauth` with scripts disabled. Completed the browser OAuth grant; a stdio handshake returned `cloudflare-api` 0.1.0 with `docs`, `search`, `execute`, `whoami`. The `cloudflare` row now targets the full API through that bridge; the app restart that loads it is still pending. |
| 2026-11-13 | Setup runbook | Added `SETUP.md`, a self-contained replication runbook (facts table, eight commands with expected output, failure table) so a fresh agent spends one file of context instead of exploring the repository. `check` now requires it; `AGENTS.md` §2 routes replication tasks to it and §8 requires updating it with any setup change. |

---

## How to update this file

At the end of any session that changes the repository:

1. Update **Snapshot** (date, counts, status).
2. Add/remove **Open questions** and **Next actions** — this file must always tell the next agent what to do.
3. Add one **Session log** row.
4. Move completed next actions out; do not leave stale TODOs.
5. Keep it under ~150 lines. If it grows, split reference detail into `docs/` and link it.
