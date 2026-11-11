# ADR-0001 — Repository is the source of truth, with explicit capture/apply

- **Status:** Accepted
- **Date:** 2026-11-11
- **Deciders:** Ayush Bhattarai

## Context

Harness configuration can be changed from two places: the DSH app (Settings, Plugins page, model pickers) and by editing files. Without a single authority, a new machine cannot be reproduced and changes silently diverge between machines.

The alternatives were:

1. Keep live files under `~/.dsh` as truth and use the repo as a backup.
2. Treat the repo as truth and make every live change flow through it.
3. Symlink everything so the repo *is* the live configuration.

Option 3 is fragile because DSH, pnpm and the plugin manager write files atomically (write-temp + rename), which replaces symlinks; option 1 makes the repo a stale snapshot.

## Decision

The **repository is the source of truth**. Live paths are deployment targets. Two explicit operations move state:

- `./bin/dsh capture` — live → repo (profile files, inventory, drift report).
- `./bin/dsh apply` — repo → live (with backups; refuses silent overwrites).

Changes made in the app are captured deliberately and reviewed as a Git diff. Changes made in the repo are deployed deliberately.

## Consequences

- Every configuration change is reviewable and reproducible.
- There is a real cost: forgetting `capture` after an app change creates drift, which `doctor` reports.
- `apply` must be conservative (`--force` + backup) to avoid destroying uncaptured work.
- If drift becomes frequent, revisit automation (watcher or pre-commit hook) in a new ADR; it was rejected for the bootstrap as unnecessary complexity.
