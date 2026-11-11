# src/host/ — engine, storage, read-only guard, transport

The Host half forks the parent session, denies every tool at execution time, persists topics, and
serves the Client through hidden commands.

## Invariants

- **One active side question per parent session**, `MAX_ACTIVE_BTW` process-wide.
- **Reserve the child id before activation**, then `ChildGuard.own(id)`; the root guard must know
  the id before any model request can emit a tool call. `attach()` adds a child-scope guard.
- **Never implement read-only with a prompt or a tool filter.** The tools stay in the request so
  the prompt prefix is identical; `ctx.tools.guard` rejects execution.
- `startActivation()` resolves on acceptance, not on the full answer. The Client needs the
  accepted child id to retain the session and stream.
- Cleanup order: persist the turn, release the guard, dispose the activation, archive the child
  best-effort, then drop the active job.
- Storage domain is `btw`, version `1`, table `topics`, key `${parentSessionId}:${topicId}`.
  Missing `storageDomain` degrades to process memory with a warning, never an ad-hoc JSON file.
- `hideInternalCommands()` filters `commands.list`; `quietInternalCommands()` drops the
  `command/run`/`command/done` pair for internal names. Both are instance-level compatibility
  shims: if a future DSH removes the method, keep the feature working and log the fallback.

## Files

| File | Responsibility |
| --- | --- |
| `engine.ts` | ask / cancel / delete / dispose, concurrency, timeout, settlement |
| `store.ts` | domain storage, topic schema, memory fallback, crash repair |
| `tool-guard.ts` | reserved child ids and execution-time denial |
| `parent-context.ts` | live partial capture, open-turn snapshot, last completed turn |
| `commands.ts` | hidden command registration and transcript/lifecycle quieting |
