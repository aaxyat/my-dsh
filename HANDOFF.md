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
| Personal plugins | 6 installed (`@local/pinned-workspaces`, `@local/btw`, and the `parallel-mcp`, `playwright-mcp`, `context7-mcp`, `cloudflare-mcp` configuration bundles, linked from `harness/plugins/`) |
| Third-party plugins | 0 |
| MCP servers | 4 (`parallel-mcp`, `playwright`, `context7`, `cloudflare`) |
| Managed artifacts | 6 + 6 personal bundles |
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
- Cloudflare docs check: `search_cloudflare_documentation` for "Workers KV binding configuration" returned `developers.cloudflare.com` pages.
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

## Next actions

Priority order:

1. **Restart DSH**, open a new session, and confirm the new global rules load (`AGENTS.md`), with `RULES.md` present at `~/.agents/`. Then run `/btw` with a question and confirm a bubble streams, Stop keeps the partial, and main transcript has no new rows.
2. Confirm the `mediaserver` host-key fingerprint out of band, then run `ssh-verify mediaserver`; install `gitleaks` + global hook chain, retention LaunchAgent, and wire `PATH`.
3. Resolve the license question (README + `LICENSE`).
4. Add the first real personal skill under `harness/skills/<name>/` using [`docs/templates/SKILL.md`](docs/templates/SKILL.md), then `./bin/dsh link`.
5. Parallel MCP is anonymous. To enable `web_research` and higher limits, change the bundle URL to `https://mcp.parallel.ai/mcp?login`, reinstall it, and complete the browser sign-in.
6. Re-run `./bin/dsh capture` after any change made in the DSH app, and commit.
7. Update `agents/bin/*` in the repo, then `python3 tools/provision_agents.py --force`; never edit `/opt/agents/bin` in place.

## Known gaps

- `/opt/agents` is provisioned and locked, but `PATH` is not wired and the retention LaunchAgent is not installed (human-owned). `preflight` reports 5 warnings.
- `newton` works end-to-end through Bitwarden. `mediaserver` is reachable but its host key is untrusted (`SHA256:RglUseR9rW45O8xzdqCJt/+p9McsC7E3r81lwnNdabE`), so authentication was not exercised; `gitleaks`/global hooks are still missing. `sshd-apply` intentionally refuses to mutate.
- Helper tests covered normal and guard paths, not large trees, cross-volume moves, or concurrent runs.
- `RULES.md` is not auto-loaded by DSH; it is a companion for composing subagent prompts and must be pasted or read explicitly.
- No personal skills exist yet; four MCP servers are installed and three were exercised with live calls. Parallel `web_research` needs sign-in; Cloudflare is the documentation server because the account API server needs OAuth; Context7 runs anonymously at lower limits.
- The personal plugin's `link:` dependency is an absolute path; it is machine-specific even though it now points inside this repo. On a target machine, `apply --with-plugins` rewrites it.
- The Playwright row hardcodes the DSH runtime Node path and `/opt/agents/tools/playwright-mcp`; its Chromium download is ~584 MB. `tools/provision_playwright_mcp.py` recreates the tool but does not rewrite the row.
- `@local/btw` was installed and selected while the current DSH process was already running. The server serves its client bundle and the bundle's unit/smoke checks pass, but the slash menu, bubble streaming, Stop/partial retention and read-only denial were not exercised through a live GUI turn; that needs the restart in Next action 1.
- The legacy pre-repo plugin directory is an identical duplicate (open question 2). Only the repo copy should be edited.
- `apply --with-plugins` could not drive pnpm inside this session's file sandbox (pnpm's store lives outside the workspace). The equivalent `pnpm add link:` command succeeded manually with full access; the script's wrapper logic is still unproven end-to-end on a fresh machine.
- `check` warns rather than fails on machine-specific `link:` dependencies, uncaptured profile edits and missing inventory entries. It also warns that the four `*-mcp` bundles have no `dsh.client.platform`; that is expected because they are configuration-only and ship no Client half.
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
| 2026-11-11 | Cleanup | Removed every `/agents` alias reference; the workspace is addressed only by `/opt/agents`. Fixed SSH auth with Bitwarden `IdentityAgent`, `~/.zshenv` and `launchctl`; recognized `newton`/`mediaserver` as MagicDNS names, added the `ControlPersist` policy, and verified `newton`. `preflight` reports 5 warnings. |
| 2026-11-11 | `/btw` plugin | Added `harness/plugins/btw/`: a Host + Web Client bundle (derived from Apache-2.0 `dsh-btw-marginalia`) for read-only `/btw` side questions, with committed `lib/`. Typechecked against 0.2.2-rc.1, 58/58 tests, build + smoke pass; linked and selected in the `desktop` profile, and the live Web server serves the client bundle. Live GUI turn still needs the restart. |
| 2026-11-11 | Parallel search | Added the `@local/parallel-mcp` configuration-only bundle, linked and selected in the `desktop` profile; `mcp-parallel` is active and exposes `web_search`, `web_fetch`, `web_decisions` and search utilities. Anonymous mode; a live search succeeded, `web_research` needs sign-in. |
| 2026-11-11 | More MCP servers | Added `playwright-mcp`, `context7-mcp` and `cloudflare-mcp` configuration bundles, all active. Provisioned Playwright MCP and Chromium under `/opt/agents/tools/playwright-mcp` with `tools/provision_playwright_mcp.py`; verified a real Playwright navigation, a Context7 library lookup and a Cloudflare docs search. |

---

## How to update this file

At the end of any session that changes the repository:

1. Update **Snapshot** (date, counts, status).
2. Add/remove **Open questions** and **Next actions** — this file must always tell the next agent what to do.
3. Add one **Session log** row.
4. Move completed next actions out; do not leave stale TODOs.
5. Keep it under ~150 lines. If it grows, split reference detail into `docs/` and link it.
