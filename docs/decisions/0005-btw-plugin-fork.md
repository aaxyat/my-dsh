# ADR-0005 — Vendor the Apache-2.0 `/btw` implementation as a personal bundle

- **Status:** Accepted
- **Date:** 2026-11-11
- **Deciders:** Ayush Bhattarai

## Context

The requested `/btw` behaviour is a read-only side question against the current session: same
system prompt, tools and completed history; tools rejected at execution time; a compact snapshot of
an in-progress turn; durable topics; streaming and cancellation; insert into the composer instead of
a fabricated branch.

An Apache-2.0 DSH Host + Web Client bundle already implements that contract
([`dsh-btw-marginalia`](https://github.com/LTP414/dsh-btw-marginalia)). Writing an equivalent from
scratch would duplicate a tested engine, guard, storage schema and client state machine, and would
take longer than the feature is worth.

The repository's rule is that **third-party** bundles are recorded in
[`harness/plugins/registry.yaml`](../../harness/plugins/registry.yaml), never vendored. That rule
protects upstream independence and repository size. It does not fit a bundle we must rename, build
against the exact installed DSH, and keep working when the upstream project moves or stalls.

## Decision

Treat the implementation as a **personal bundle** under
[`harness/plugins/btw/`](../../harness/plugins/btw/):

- Keep the Apache-2.0 source, `LICENSE`, `NOTICE` and third-party notices.
- Rename package and user-visible identifiers to `@local/btw`; keep the internal architecture.
- Commit the built `lib/` so installation never needs Node or a build step.
- Install it with `./bin/dsh apply --with-plugins` as a `link:` dependency and select it in
  `dsh.profile.bundles`.
- Typecheck, unit-test and smoke-test it against the installed DSH version before recording it.

## Consequences

- `/btw` has one canonical, reviewable source in this repository and can be fixed without waiting
  for an upstream release.
- We own compatibility: a DSH upgrade can break the command/transport shims or the Client slots, and
  it is our job to update the source, rebuild `lib/`, and rerun the checks.
- Upstream changes are merged selectively; this is a fork, not a dependency, so there is no automatic
  upgrade path.
- `lib/` is ~1.3 MB of committed build output and the secret scan now covers it. Rebuild and commit
  it whenever `src/` changes.
- The directory is Apache-2.0 while the repository root has no license yet; see open question 6 in
  [`HANDOFF.md`](../../HANDOFF.md).
