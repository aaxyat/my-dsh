# Architecture — how DSH loads this configuration

Verified against **DSH desktop 0.2.2-rc.1** by reading the shipped bundles (`dsh-agent-instructions`, `dsh-skill-filesystem`, `dsh-agent-preset`, `dsh-plugin-manager`, `dsh-mcp-client`) and the live profile on 2026-11-11. If a future DSH release changes a path or precedence rule, update this document and `docs/troubleshooting.md` in the same commit.

## 1. Two home directories

| Root | Default | Env override | Holds |
|---|---|---|---|
| DSH home | `~/.dsh` | `DSH_HOME` | profiles, credentials, sessions, storages, runtime toolchains |
| Agents home | `~/.agents` | `DSH_AGENTS_HOME` | cross-tool agent configuration: `AGENTS.md`, `skills/` |

DSH resolves both from the process environment. A profile row cannot redirect them; this repository therefore treats them as machine contract, not configuration.

```
~/.dsh/
  profiles/desktop/         # the active composition
  .credentials.yaml         # secret refs — NEVER copied into this repo
  sessions/                 # conversation state — not configuration
  storages/                 # workspace index — machine state
  dsh-runtimes/             # bundled node, pnpm, python
~/.agents/
  AGENTS.md                 # user-global instructions (symlink to repo)
  RULES.md                  # compact rules for subagent prompts (symlink, not auto-loaded)
  skills/<name>/SKILL.md    # user skills (symlinks to repo)
```

## 2. Profiles and composition order

A profile is a directory with four meaningful files:

| File | Role |
|---|---|
| `package.json` | `dsh.profile.bundles` (ordered) and third-party bundle dependencies |
| `cordis.patch.yml` | the user's patch layer: settings, tool rows, model providers |
| `pnpm-workspace.yaml` | pnpm settings (`nodeLinker: hoisted`, `allowBuilds`) |
| `cordis.yml` | generated empty skeleton; do not edit |

Resolution order, each layer overriding the previous by plugin `id`:

```
1. @deepseek-ai/dsh-base        ┐
2. @deepseek-ai/dsh-web-app     │ bundles, in package.json order (later wins)
3. ...other selected bundles    ┘
4. cordis.patch.yml               ← the file this repo owns
5. home / invocation patches      ← written by the app; higher priority than (4)
```

A patch entry can:

- override an existing row's `config` by `id` (optionally asserting `name`),
- set `disabled: true`,
- `insert` a list of new rows,
- use `!!js` expressions for computed values.

**Implication for this repo:** `harness/profile/desktop/cordis.patch.yml` is powerful but not absolute. If a setting seems ignored, check whether a home/invocation patch overrides it ([troubleshooting](troubleshooting.md#a-profile-setting-is-ignored)).

## 3. Bundles and plugins

A bundle is an npm package that declares a patch and optionally host/client entry points:

```json
{
  "name": "@local/example",
  "dsh": {
    "bundle": { "patch": "./cordis.patch.yml" },
    "client": { "platform": "web", "immediately": true, "inject": ["..."] }
  },
  "exports": { ".": "./index.js", "./client": "./client.js" }
}
```

- **Host half** (`index.js`) exports `apply(ctx)` and runs in-process, outside the workspace sandbox.
- **Client half** (`client.js`) registers UI through `window.__ModuleLoader__.load({ id, factory })`.
- Third-party bundles are installed as profile dependencies by the plugin manager (`pnpm add <spec>`) and enabled by adding their name to `dsh.profile.bundles`.
- Personal bundles are installed as links: `pnpm add link:/absolute/path` inside the profile directory.

This repo:

| Kind | Stored where | Installed how |
|---|---|---|
| Personal bundle | `harness/plugins/<name>/` | `./bin/dsh apply --with-plugins` (`link:` dependency) |
| Third-party bundle | not vendored; recorded in `harness/plugins/registry.yaml` | install in the app, then `capture` |
| Built-in bundle | shipped with DSH | `package.json` bundle list only |

## 4. Instruction files (`AGENTS.md`)

The loader (`dsh-agent-instructions`) builds one baseline from, in order:

1. **User-global:** `~/.dsh/AGENTS.md`, then `~/.agents/AGENTS.md`
2. **Project:** for each directory from the project root down to the working directory:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `AGENTS.local.md`
   - `CLAUDE.local.md`

Rules that matter:

- The project root is the nearest ancestor containing a **`.git`** directory.
- Later files are **more specific** and therefore take precedence in conflict.
- Files with identical trimmed content are deduplicated — creating both `~/.dsh/AGENTS.md` and `~/.agents/AGENTS.md` renders once.
- Content is injected as a system-reminder message, budgeted by the profile's `maxBytes`; oversized sets omit the broadest files and truncate the most specific one.
- Instructions are re-read during the session after `read`/`write`/`edit` touches, so edits apply without restart.
- `AGENTS.local.md` is for machine-local, uncommitted notes; this repo ignores `*.local.md`.

**This repo:** `harness/instructions/AGENTS.md` → symlink at `~/.agents/AGENTS.md`. It is the base layer for every project; project-level `AGENTS.md` files (including the one at this repo's root) override it.

`harness/instructions/RULES.md` → symlink at `~/.agents/RULES.md` is a **companion**, not a discovery file: DSH does not load it automatically. `AGENTS.md` points to it and requires rules 1–7 to be pasted into subagent prompts. Keep the two consistent; the manual owns procedures, the rules file owns the compact policy.

## 5. Skills

A skill is either a directory containing `SKILL.md` or a flat `<name>.md`, discovered from these roots:

| Rank | Root | Meaning |
|---:|---|---|
| 100 | `<project>/.dsh/skills` | highest priority |
| 200 | `<project>/.agents/skills` | |
| 300 | `customSkillDirs` (profile config) | |
| 400 | `~/.dsh/skills` | |
| 500 | `~/.agents/skills` | **used by this repo** |
| low | bundled skills shipped with DSH profiles | lowest priority |

Lower rank is consulted first, so a project skill shadows a user-global one and a user skill shadows a bundled one. Directory names and skill names are validated (`[a-z0-9-]` style kebab-case); a `SKILL.md` declares frontmatter:

```yaml
---
name: office-docx
description: Create, read, edit, and validate Word documents (.docx).
whenToUse: When the user asks for a Word document.
---
```

Only `name` and `description` are always required; `whenToUse`/`invocation`/`metadata` are optional. The body is loaded on demand when the skill is invoked, so keep `SKILL.md` short and move bulk into `references/`.

The loader watches roots (including symlinked directories) and picks up edits live.

## 6. Tools

"Tools" is not a separate config surface in DSH; tools come from three places:

1. **Bundled tool plugins** in the base composition (bash, filesystem, web, subagents, jobs, scheduling, goals, workflows, present…), enabled per profile.
2. **Bundles that add tools** — MCP clients, personal tool bundles, experimental tool plugins.
3. **MCP servers**, each mounted as its own `dsh-mcp-client` row.

Tool enablement and permissions therefore live in the profile patch (rows such as `tool-plugin-manager`, `permission-presets`) and in each session's permission mode. `harness/tools/README.md` maps the surfaces; `harness/mcp/servers.yaml` inventories MCP servers.

Separately, the machine-level helper workspace described in `AGENTS.md` §7 is tracked in `agents/` and installed to `/opt/agents` by `tools/provision_agents.py`. It is not part of the DSH composition and is not deployed by `bin/dsh apply`.

## 7. MCP servers

Each server is one plugin instance in the profile patch:

```yaml
- id: mcp-github
  name: "@deepseek-ai/dsh-mcp-client"
  config:
    transport: stdio            # or: streamable-http
    serverName: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "$GITHUB_TOKEN"
```

Tool names become `mcp__<serverName>__<toolName>`; `serverName` is unique per agent scope and limited to `[A-Za-z0-9_-]{1,32}`. HTTP transport uses `url` + `headers` instead of `command`/`args`/`env`. Credentials stay in the environment or DSH's credential store — never in the patch file.

A row can live directly in the profile patch, or be inserted by a **configuration-only bundle** under `harness/plugins/<name>/`. Use the bundle form when the server must be installed into an already-running desktop app: the plugin manager applies a bundle live, while a new profile-patch row is read at startup. The `*-mcp/` bundles ([`parallel-mcp/`](../harness/plugins/parallel-mcp/), [`playwright-mcp/`](../harness/plugins/playwright-mcp/), [`context7-mcp/`](../harness/plugins/context7-mcp/), [`cloudflare-mcp/`](../harness/plugins/cloudflare-mcp/)) are examples; each bundle patch inserts the same `dsh-mcp-client` row.

## 8. Credentials

`~/.dsh/.credentials.yaml` is written `0600` by DSH and holds named references such as `DEEPSEEK_API_KEY` and `OPENCODE_GO_API_KEY`. Provider rows in the profile refer to them by **environment-variable name** (`apiKeyEnv: OPENCODE_GO_API_KEY`).

This repository never stores the file, its values, or derived tokens. Restoring a machine means re-entering credentials through DSH's UI or the OS environment. See [secrets.md](secrets.md).

## 9. What this repository controls

| Managed | Not managed |
|---|---|
| User-global instructions | DSH application binaries and bundled runtime |
| Personal skills | Session transcripts and workspace index |
| Profile patch, bundle selection, pnpm settings | `node_modules`, lockfiles, downloaded bundles |
| Personal plugin source | Third-party plugin source (recorded only) |
| MCP inventory and patch rows | Credentials, API keys, OAuth tokens |
| Capture/apply/validate tooling | Caches, logs, generated `cordis.yml` |

## 10. Version sensitivity

Paths and precedence above are stable across the 0.2.x line, but patch schema and bundle names can change between releases. When upgrading DSH:

1. `./bin/dsh capture` and review the profile diff.
2. Run `./bin/dsh check` and `./bin/dsh doctor`.
3. Open a session and confirm: instructions load, skills appear, profile settings apply, plugins start.
4. Record the version bump in `machine/inventory.json` (via capture), `HANDOFF.md`, and `CHANGELOG.md`.
