# Layout — where every file belongs

One artifact, one home. If something does not fit the table below, write the proposal in `HANDOFF.md` before creating a new top-level directory.

## Tree

```
.
├── AGENTS.md                     repo-specific rules loaded by DSH
├── HANDOFF.md                    living status, decisions, next actions
├── README.md                     orientation, quick start, commands
├── CHANGELOG.md                  user-visible history
├── Makefile                      thin wrappers over bin/dsh
├── .env.example                  credential variable names only
├── .editorconfig                 formatting contract
├── .gitignore                    secrets, state, noise
├── .github/workflows/
│   └── validate.yml              CI: ./bin/dsh check
├── bin/
│   └── dsh                       CLI entry point (finds Python, execs tools)
├── tools/
│   ├── dshctl.py                 capture / apply / link / check / doctor
│   └── provision_agents.py       install agents/ into /opt/agents (idempotent)
├── agents/
│   ├── README.md                 workspace layout, helper reference, activation
│   └── bin/                      preflight, manifest, rm, gate-rm, undo-rm,
│                                 git-snapshot, ssh-probe, ssh-verify,
│                                 sshd-apply, retention
├── docs/
│   ├── architecture.md           DSH load semantics (authoritative reference)
│   ├── layout.md                 this file
│   ├── workflow.md               change lifecycle and recipes
│   ├── restore.md                new-machine procedure
│   ├── secrets.md                credential policy
│   ├── inventory.md              what machine/inventory.json means
│   ├── troubleshooting.md        symptom -> cause -> fix
│   ├── decisions/                ADRs (numbered, immutable once accepted)
│   └── templates/                SKILL.md, project AGENTS.md, ADR
├── harness/
│   ├── manifest.json             every deployed artifact + deploy mode
│   ├── instructions/
│   │   ├── AGENTS.md             user-global manual (auto-loaded)
│   │   └── RULES.md              compact rules 1-7 (subagent prompts, not auto-loaded)
│   ├── profile/
│   │   ├── README.md
│   │   └── desktop/
│   │       ├── cordis.patch.yml
│   │       ├── package.json
│   │       └── pnpm-workspace.yaml
│   ├── skills/
│   │   ├── README.md
│   │   ├── packs.json            third-party packs: repo, pinned commit, selection
│   │   └── <skill-name>/
│   │       ├── SKILL.md
│   │       └── references/       optional, loaded on demand
│   ├── plugins/
│   │   ├── README.md
│   │   ├── registry.yaml         installed third-party bundles
│   │   └── <plugin-name>/        personal bundle source
│   ├── mcp/
│   │   └── servers.yaml          MCP inventory (rows live in the patch)
│   └── tools/
│       └── README.md             where DSH tools come from
└── machine/
    └── inventory.json            generated snapshot (do not hand-edit)
```

## Decision table

| You are adding… | Put it in | Then |
|---|---|---|
| A rule that should apply to every project | `harness/instructions/AGENTS.md` (manual) or `RULES.md` (compact policy) | `./bin/dsh link` |
| A rule for this repo only | `AGENTS.md` | commit |
| A rule for one project | that project's `AGENTS.md` (use `docs/templates/project-AGENTS.md`) | commit in that project |
| A reusable capability with instructions | `harness/skills/<name>/SKILL.md` | `./bin/dsh link`, new session |
| Bulk skill reference material | `harness/skills/<name>/references/` | — |
| A third-party skill | `harness/skills/packs.json` → `include` (never the source itself) | `./bin/dsh skills sync` |
| A personal bundle (host or UI code) | `harness/plugins/<name>/` | manifest entry, `apply --with-plugins` |
| A third-party bundle | `harness/plugins/registry.yaml` entry | install in app, `capture` |
| An MCP server | profile patch row **and** `harness/mcp/servers.yaml` | `apply`, restart |
| A model/provider | `harness/profile/desktop/cordis.patch.yml` (`llm-*` row) | `apply` |
| A tool policy / permission default | `harness/profile/desktop/cordis.patch.yml` | `apply`, restart |
| New automation for this repo | `tools/dshctl.py` subcommand + `bin/dsh` | update README/workflow |
| A machine-level helper for `/opt/agents` | `agents/bin/<name>` + `agents/README.md` | `python3 tools/provision_agents.py --force` |
| A structural decision | `docs/decisions/NNNN-slug.md` | link from HANDOFF |
| Machine facts | `machine/inventory.json` (generated) | `./bin/dsh capture` |
| Anything secret | **nowhere in this repo** | see `docs/secrets.md` |

## Naming

- Directories and files: `kebab-case`, lower case, ASCII.
- Skill directory name should equal the skill's `name` in frontmatter.
- Plugin directory name should equal the last segment of its package name (`pinned-workspaces` for `@local/pinned-workspaces`).
- ADRs: `NNNN-short-title.md`, four digits, never renumbered.
- Docs: one topic per file, no `misc.md` or `notes.md`.

## Formats

| Content | Format | Why |
|---|---|---|
| Anything DSH reads | YAML / JSON as the app expects | native format |
| Manifest, inventory | JSON | parseable by stdlib Python, no dependencies |
| Human docs | Markdown | reviewable diffs |
| Scripts | POSIX `sh` wrapper + Python 3 stdlib | works on a fresh Mac and in CI |

## What never goes in

- Credentials, tokens, private keys, cookies, `.env` files with values.
- Session transcripts, workspace indexes, caches, `node_modules`, lockfiles generated by pnpm.
- DSH application binaries or runtime toolchains.
- Vendored third-party plugin source (link or record the version instead).
- Machine-specific absolute paths outside `machine/inventory.json` and `~`-relative deployment targets.
