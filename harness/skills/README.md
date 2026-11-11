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
