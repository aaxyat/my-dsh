# ADR-0002 — Symlink read-only artifacts, copy app-written files

- **Status:** Accepted
- **Date:** 2026-11-11
- **Deciders:** Ayush Bhattarai

## Context

Deployment could use symlinks or copies for every artifact. The artifacts differ in who writes them:

- `~/.agents/AGENTS.md` and `~/.agents/skills/*` are **read** by DSH. Nothing writes them except the user.
- `~/.dsh/profiles/desktop/*` is **written** by DSH, the Settings page and pnpm (atomic rename, dependency updates, lockfiles).

A symlink is the best single-source-of-truth mechanism for read-only paths: editing the live file edits the repo, and a new skill needs one link. For app-written paths, an atomic write replaces the symlink with a regular file, silently breaking the source-of-truth guarantee.

## Decision

- **Symlink** instruction files and skill directories into `~/.agents/`.
- **Copy** profile files (`cordis.patch.yml`, `package.json`, `pnpm-workspace.yaml`) and reconcile them with `capture`/`apply`.
- Never symlink anything the app or pnpm may rewrite.

## Consequences

- Editing a skill or global instruction is live immediately; `capture` is not needed for those surfaces.
- Profile changes require the capture/apply step and can conflict; the tool backs up and refuses to clobber silently.
- A symlinked skill means deleting the repo file removes it from DSH; that is intended and documented in `docs/restore.md`.
- Skills are discovered through symlinks because the loader enables `watchFollowSymlinks`; if a future DSH release stops following links, switch skills to copy mode in `harness/manifest.json`.
