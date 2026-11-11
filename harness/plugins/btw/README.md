# @local/btw — read-only `/btw` side questions

Ask a question beside the current conversation without changing it. `/btw` lets the model
see the session it is already in — system prompt, tools, completed history, and a compact snapshot
of the turn that is running — but the answer stays in a composer bubble and never enters the main
transcript.

This is a **Host + Web Client bundle** for DeepSeek Harness. It is a renamed, locally maintained
derivative of [`dsh-btw-marginalia`](https://github.com/LTP414/dsh-btw-marginalia) (Apache-2.0);
see [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## What it does

| Contract | How |
| --- | --- |
| Same conversation | The side turn forks the current session, so it inherits the system prompt, the tool catalog, and completed history. |
| Read-only, enforced | Tools stay in the request to preserve the prompt prefix, but `ctx.tools.guard` rejects every tool call for the reserved child session. This is execution-time enforcement, not a prompt request. |
| In-flight context | While the main turn is running, the side prompt receives a capped snapshot of the current user request, recent tool calls/results, and the live assistant partial. |
| Topics and history | Every question is stored with its status and answer. A follow-up replays the topic and sees the parent conversation as it is now. |
| Streaming and cancellation | The browser retains the child session, renders partial text, and keeps the partial when you stop. |
| No fabricated branch | DSH has no public assistant-message injection API. **Insert into composer** is the safe replacement. |

`/btw` with no argument opens topic history. `/btw <question>` asks in a bubble. The history button
in the composer's left tool row opens the same list.

## Install

This directory is a personal bundle in the `my-dsh` repository. Install it into the `desktop`
profile through the repository CLI:

```sh
./bin/dsh apply --with-plugins
```

That adds a `link:` dependency and selects `@local/btw` in `dsh.profile.bundles`. Restart DSH
afterwards. Build artifacts are committed, so installation does not need Node.

## Build and test

The plugin is TypeScript built with esbuild. Use the Node bundled with DSH when `node` is not on
`PATH`:

```sh
NODE=~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node
"$NODE" node_modules/esbuild/bin/esbuild --version   # availability check
"$NODE" node_modules/vitest/vitest.mjs run           # 58 unit tests
"$NODE" scripts/build.mjs                           # lib/index.js + lib/client.js + lib/types
"$NODE" scripts/smoke.mjs                           # built-artifact load + /btw claim
```

`npm run check` runs the unit tests, build, and smoke test when an `npm`/`node` pair is available.

> **macOS code-signing note:** the DSH runtime Node is hardened and refuses to `dlopen` ad-hoc
> native modules from npm (vitest's Rollup binding). For local tests, copy it to scratch and
> re-sign the copy with `codesign --force --sign - /tmp/dsh-node-test`, then run `vitest` with that
> copy. The plugin bundles themselves have no native dependencies.

Commit `lib/` whenever `src/` changes; DSH loads the built bundle directly.

## Design

```
/btw question
  → Client input trigger claims the line
  → Host `btw-ask` (authenticated command RPC, lifecycle suppressed)
      reserve child id → guard the id → fork the parent
      append one user-role <btw> prompt
      persist a running turn
  → Client retains the child session and follows its Chat target
  → Host stream capture keeps partial text; cancellation persists it
  → Host persists complete/cancelled/error; child is archived best-effort
```

- **Prompt prefix:** the fork inherits completed turns; `/btw` appends exactly one user-role
  message. It never changes the system prompt, tool table, persona, or preset.
- **Transport:** hidden Host commands (`btw-ask`, `btw-list`, `btw-get`, `btw-cancel`, `btw-delete`)
  over the authenticated `commands.execute` RPC. No new HTTP route. The command directory and
  session lifecycle are filtered so the internal transport does not appear in the main transcript.
- **Storage:** a `storageDomain` table named `btw`, keyed by `${parentSessionId}:${topicId}`. When
  the domain is absent, history degrades to process memory and logs a warning.
- **Limits:** 8k question, 8k quote, 64k replayed topic history, 256 KiB answer, 50 topics per
  session, 200 turns per topic, 4 active side questions process-wide, 10-minute watchdog.

## Security properties

- No HTTP routes. All reads/writes go through the authenticated command RPC.
- The side child can never execute a tool, including `send_message`.
- No raw HTML, remote images, or unsanitized Markdown extensions are rendered in answers.
- Host errors are reduced to one bounded, control-character-free line.
- The plugin refuses to start from a subagent view; side questions are a main-session feature.
- Child sessions inherit the parent's sandbox and permission model; the guard removes tool
  execution, it does not widen permissions.

## Known limitations

- **Not truly ephemeral.** A fork creates a durable child session. The plugin archives it after
  completion when the workspace registry is available; it cannot make the Host forget it.
- **No branch.** DSH exposes no public assistant-message injection/branch API.
- **History replay is text.** The child receives one user prompt with a `<btw-history>` section;
  it does not replay role-level messages.
- **Open-turn context is a snapshot.** It is taken when you ask and capped; it may be stale if the
  main turn advances while the side answer is generated.
- **Archive is best-effort.** A failed archive is logged; the side history is still correct.

## Layout

```
src/index.ts          Host entry and wiring
src/shared.ts         protocol, limits, prompt, sanitization
src/host/             engine, storage, guard, stream capture, hidden commands
src/client/           input trigger, store, bubble, history, Markdown, styles
tests/                unit and wiring tests (58)
scripts/              esbuild build and built-artifact smoke
lib/                  committed build output loaded by DSH
```

## License

Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
