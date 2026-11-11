# Tools

DSH has no separate "tool configuration" file. Tools reach a session through three surfaces, all of which this repository already covers:

| Surface | What it provides | Managed in |
|---|---|---|
| **Bundled tool plugins** | `bash`, `read`/`write`/`edit`, search, web, jobs, subagents, workflows, goals, scheduling, `present`, `working_directory`, … | Profile patch rows + per-session permission mode |
| **Bundle-provided tools** | Tools added by personal or third-party bundles (e.g. session query, agent team, terminal) | `harness/plugins/`, `harness/plugins/registry.yaml` |
| **MCP servers** | External tool servers namespaced `mcp__<server>__<tool>` | `harness/profile/desktop/cordis.patch.yml` + `harness/mcp/servers.yaml` |

## Where to change tool behaviour

- **Enable/disable a tool plugin:** add or edit its row in the profile patch (`disabled: true|false`). Built-in ids are visible in the live profile and the Plugins page.
- **Permissions/sandbox:** DSH permission modes are session-level; profile defaults live in prompt/permission-preset rows. Do not try to encode a permission policy as a static file here — record it in the patch and test it.
- **Add a tool with custom logic:** build a personal bundle (`harness/plugins/<name>/`) that registers a tool on `ctx.tools`; see the bundle skill in DSH's bundled `cordis-plugin-development` skill.
- **Add an external tool server:** MCP row (see `harness/mcp/servers.yaml`).

## Rules

- A tool that executes host code is a security boundary; document why it is enabled in `registry.yaml` or the patch comment.
- Tools that need secrets take them from the environment or DSH credential store, never from a committed value.
- When a tool changes the machine (writes outside the workspace, installs software, pushes Git), mention it in the skill/instructions that trigger it.

## What not to put here

Do not copy DSH tool implementations into this repository. This directory is documentation only; the deployable artifacts are the profile patch, bundles and MCP rows.
