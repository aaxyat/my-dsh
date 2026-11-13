# Skills

Personal skills live here as directory bundles. Each first-level directory is symlinked into `~/.agents/skills/<name>` by `./bin/dsh link`, where DSH discovers it (user-agents root, rank 500).

```
harness/skills/<kebab-name>/
├── SKILL.md          required; YAML frontmatter + instructions
├── references/       optional; read only when the skill asks for it
└── scripts/          optional; deterministic helpers
```

Start from [`../../docs/templates/SKILL.md`](../../docs/templates/SKILL.md).

## Rules

- Directory name = frontmatter `name` = kebab-case.
- `description` is always visible to the model; make it a precise trigger, not a summary of the body.
- Keep `SKILL.md` under ~8 KB; large material belongs in `references/`.
- No secrets, no machine-specific absolute paths.
- A skill must be usable without this repository (it may reference bundled tools, not repo-local files).

## Precedence

Lower rank wins: project `.dsh/skills` (100) → project `.agents/skills` (200) → custom dirs (300) → `~/.dsh/skills` (400) → `~/.agents/skills` (500) → bundled skills. A project skill can therefore shadow a personal one; name skills distinctly.

## Adding one

```sh
mkdir -p harness/skills/my-skill
cp docs/templates/SKILL.md harness/skills/my-skill/SKILL.md
$EDITOR harness/skills/my-skill/SKILL.md
./bin/dsh check
./bin/dsh link
```

Open a new session to confirm discovery. DSH watches skill roots, so later edits are picked up live.

## Third-party packs

Skills from other repositories are installed **without vendoring them**. [`packs.json`](packs.json) records where each pack comes from and which of its skills are wanted; `./bin/dsh skills sync` does the rest:

1. clones each pack at its pinned commit into `<agentWorkspace.target>/tools/skill-packs/<pack>/` (`/opt/agents/tools/skill-packs/` on this machine),
2. links **only** the selected skill directories into `~/.agents/skills/<name>`.

The clone keeps the upstream `LICENSE`, history and README, so nothing is redistributed and a re-sync is a `git fetch`, not a re-download.

| Pack | Upstream | Pinned | License | Selected |
|---|---|---|---|---|
| `mattpocock` | [mattpocock/skills](https://github.com/mattpocock/skills) | `5863806dd4e1` | MIT | 20 engineering and productivity workflows |
| `anthropic` | [anthropics/skills](https://github.com/anthropics/skills) | `2c5958ecac7c` | Apache-2.0 | 7: skill authoring, MCP, design, docs, web testing |
| `cursor` | [cursor/plugins](https://github.com/cursor/plugins) | `24621dbcc59e` | MIT | 16 self-contained PR/CI/review workflows |

`packs.json` also records every excluded directory with a one-line reason, so the next reviewer sees why something is missing instead of re-deciding it. One exclusion is a defect rather than a judgement call: `check-agent-compatibility` writes `description: Run the ... pass: scanner score` — an unquoted colon-space, which is invalid YAML, so a strict parser drops the file. Sync refuses that shape instead of linking a skill that would never appear (`frontmatter_defect`), so re-add it only after upstream quotes the value.

`obra/superpowers` is deliberately **not** installed: 13 of its 15 skills already ship with the Aegis bundle under identical names, and because `~/.agents/skills` (rank 500) outranks bundled skills (600), installing it would silently shadow Aegis's DSH-adapted copies and break its routing. The `skipped` entry in `packs.json` records the full reasoning and when to revisit it.

### Commands

```sh
./bin/dsh skills sync              # clone/update pinned packs, then link (default: prune)
./bin/dsh skills sync --dry-run    # show what would change
./bin/dsh skills sync --offline    # use the existing clones; never touch the network
./bin/dsh skills status            # pack revisions, link counts, stale/missing links
```

`apply` and `link` run `skills sync` as part of deployment; pass `--no-packs` to skip it (offline or air-gapped runs).

### Safety rules

- **Never overwrites real files.** A non-symlink already sitting at `~/.agents/skills/<name>` is a conflict: sync reports it and leaves it alone. Delete or move it yourself, then re-run.
- **Prunes only its own links.** A link is removed when it points inside the pack clone but is no longer selected. Links into this repository and links made by hand are untouched. `--no-prune` keeps everything.
- **Fails closed.** Any error (pack missing, wrong revision, `SKILL.md` absent, duplicate name) aborts before a single link changes.
- **Names are global.** A pack skill name must be unique across packs, must not equal a personal skill in `harness/skills/`, and must not shadow a bundled skill. `check` enforces the first two; the third is why `packs.json` lists packs that were considered and rejected.
- **Directory name = `name`.** Sync refuses a skill whose frontmatter `name` disagrees with its directory, because the link name comes from the directory.

### User-invocable only

Ten selected skills declare `disable-model-invocation: true` upstream, which DSH honours: the model is not shown them and will not route to them on its own, but you can invoke them by name. They are the author's explicit phase commands — `handoff`, `implement`, `improve-codebase-architecture`, `retro`, `teach`, `to-questionnaire`, `to-spec`, `to-tickets`, `wait-what`, `thermo-nuclear-code-quality-review`.

### Updating a pack

```sh
git -C /opt/agents/tools/skill-packs/<pack> fetch --depth 1 origin <new-sha>
git -C /opt/agents/tools/skill-packs/<pack> diff --stat <old> <new> -- <selected paths>
```

Review the upstream diff, then change `commit` (and `include`/`exclude` if a skill was added, renamed or removed) in [`packs.json`](packs.json), run `./bin/dsh skills sync --dry-run`, then `./bin/dsh check` and `./bin/dsh skills sync`. Bump one pack per commit.

### Adding a pack

Add one object to `packs` in [`packs.json`](packs.json) with `id`, `title`, `repo`, a full 40-character `commit`, `license`, `added`, `include` (repo-relative directories that contain a `SKILL.md`) and `exclude` (path → reason). Then `./bin/dsh check` validates it and `./bin/dsh skills sync --dry-run` shows what would be linked.
