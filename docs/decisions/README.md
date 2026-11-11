# Architecture decision records

Short, numbered, immutable records of decisions that shape this repository. A later ADR can supersede an earlier one; do not edit accepted ADRs except to fix typos or add a `Superseded by` line.

| # | Title | Status |
|---|---|---|
| [0001](0001-repo-as-source-of-truth.md) | Repository is the source of truth, with explicit capture/apply | Accepted |
| [0002](0002-symlink-read-only-copy-app-written.md) | Symlink read-only artifacts, copy app-written files | Accepted |
| [0003](0003-secrets-never-committed.md) | Secrets never enter the repository | Accepted |
| [0004](0004-json-manifest-stdlib-tooling.md) | JSON manifest and stdlib-only tooling | Accepted |
| [0005](0005-btw-plugin-fork.md) | Vendor the Apache-2.0 `/btw` implementation as a personal bundle | Accepted |

## Writing one

Use [`../templates/ADR.md`](../templates/ADR.md). Number monotonically, name `NNNN-short-title.md`, keep it under one page. Record context, the decision, alternatives and consequences — not implementation details (link the files instead).
