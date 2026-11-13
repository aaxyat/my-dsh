# AGENTS.md — working rules for `my-dsh`

This file is loaded by DeepSeek Harness whenever the working directory is inside this repository. It governs **work on this repo**, not the user's general working style (that lives in `harness/instructions/AGENTS.md`).

## 1. What this repository is

The canonical, portable source of truth for one person's DeepSeek Harness (DSH) setup:

- user-global instructions (`harness/instructions/`)
- profile configuration (`harness/profile/desktop/`)
- personal skills (`harness/skills/`)
- personal and third-party plugins (`harness/plugins/`)
- MCP servers (`harness/mcp/`)
- tooling to capture, deploy and validate all of it (`bin/`, `tools/`)

It is **not** the DSH source tree and **not** an application. Do not add product code here unless it is harness tooling.

## 2. Start every session by

1. Reading [`HANDOFF.md`](HANDOFF.md) — current state, open questions, next actions.
2. Reading [`docs/architecture.md`](docs/architecture.md) if the task touches configuration semantics.
3. Running `./bin/dsh check` and `git status --short --branch`.
4. Checking that the working tree is clean or that you understand every pending change.

**Exception — replication tasks.** If the task is "set up this machine", "replicate this setup" or "restore on a new host", read [`SETUP.md`](SETUP.md) instead of this list and follow it. It is deliberately self-contained so that a fresh agent spends one file of context, not an exploration.

If `HANDOFF.md` and the code disagree, the code wins — then fix `HANDOFF.md`.

## 3. The one rule that matters

**Never commit a secret.** Not in a config file, skill, plugin, test fixture, commit message or inventory.

- Live credentials belong in `~/.dsh/.credentials.yaml` or the user's environment.
- Config references credentials by name only (`apiKeyEnv: OPENCODE_GO_API_KEY`).
- `.env` is ignored; only `.env.example` is committed.
- If you see a key-like string, stop and report it instead of committing.

Full policy: [docs/secrets.md](docs/secrets.md).

## 4. Source-of-truth discipline

| Situation | Do this |
|---|---|
| User changed a setting in the DSH app | `./bin/dsh capture`, review `git diff`, commit |
| User edited a repo file | `./bin/dsh apply` (or `link` for skills/instructions), then `doctor` |
| Live file differs and user is unsure | Stop. Show both sides with a diff. Do not guess. |
| Adding a new deployed artifact | Add it to `harness/manifest.json` first, then implement |
| Renaming/moving an artifact | Update manifest, docs referenced by it, and `HANDOFF.md` in the same commit |

`apply` refuses to overwrite a differing live file without `--force`. Treat that refusal as a design signal, not an obstacle.

## 5. Placement

- Global instructions → `harness/instructions/AGENTS.md`
- Project-specific instruction templates → `docs/templates/project-AGENTS.md`
- A skill → `harness/skills/<kebab-name>/SKILL.md` (+ optional `references/`, `scripts/`)
- A personal plugin/bundle → `harness/plugins/<name>/` with a valid `package.json` and `dsh.bundle.patch`
- A third-party plugin → add to `harness/plugins/registry.yaml`, do not vendor it
- MCP server → row in `harness/profile/desktop/cordis.patch.yml` **and** `harness/mcp/servers.yaml`
- New harness tooling → `tools/dshctl.py` (subcommand) + `README.md`/`docs/` update
- Decisions with lasting structural impact → `docs/decisions/NNNN-*.md`

If a file does not fit one of these, propose a location in `HANDOFF.md` before creating a new top-level directory.

## 6. Conventions

- **Shell**: POSIX `sh` for wrappers, Python 3 stdlib for logic. No third-party Python packages.
- **Formatting**: UTF-8, LF, two-space indentation for YAML/JSON, final newline. `.editorconfig` enforces this.
- **Naming**: lower-case kebab-case for files and skill/plugin directories; `AGENTS.md`/`HANDOFF.md`/`README.md` keep their canonical names.
- **Markdown**: relative links, one H1 per file, no emoji headers. Every link must resolve — `check` verifies this.
- **Commits**: Conventional Commits (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`), imperative subject ≤ 72 chars. One logical change per commit.
- **Branches**: work on `main` for small changes; use `feat/<slug>` when a change needs review or is multi-step.

## 7. Verification before you say "done"

Minimum for every change:

```sh
./bin/dsh check
```

When the change affects deployment or the live machine:

```sh
./bin/dsh apply --dry-run
./bin/dsh doctor
```

Rules:

- Do not claim a command succeeded without showing/observing its result.
- `check` must pass with zero errors (warnings may be reported but must be explained).
- If you could not run a verification step, say so explicitly and why.
- Never silence a failing check by weakening the check without user agreement.

## 8. Documentation duties

Every consequential change updates, in the same commit:

1. `HANDOFF.md` — state, decisions, next actions, session log entry.
2. `CHANGELOG.md` — under `## [Unreleased]` for user-visible changes.
3. The relevant `docs/` page (or an ADR for structural decisions).
4. `harness/manifest.json` — if any deployed artifact changed.
5. [`SETUP.md`](SETUP.md) — if a setup step, path, command, version or §1 fact changed. It is the single runbook a fresh agent follows; a stale step costs the next machine a full re-discovery.

Do not create new status documents. `HANDOFF.md` is the single living status file; everything else is reference material. `SETUP.md` is a runbook, not a status file — it describes the procedure, never the current state.

## 9. Destructive actions

Require explicit confirmation from the user before:

- `git push --force`, history rewrite, branch deletion
- deleting or rewriting `~/.dsh` state, sessions or credentials
- changing repository visibility or ownership
- installing a plugin that runs host code (it executes outside the workspace sandbox)

Do not ask for confirmation on routine reversible work (editing docs, running `check`, creating a commit).

## 10. When requirements are ambiguous

Ask one focused question with a recommended default. Do not invent user preferences, model providers or plugins. If the ambiguity is small and reversible, choose the conservative option and record it in `HANDOFF.md`.
