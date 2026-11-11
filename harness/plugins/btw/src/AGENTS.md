# src/ — shared core and the two plugin halves

`src/index.ts` is the Host entry. `src/shared.ts`, `src/limits.ts`, and `src/random.ts` are
imported by both halves; keep them free of DOM and Node runtime imports.

## Invariants

- `src/shared.ts` is the only protocol source: command names, request parsing, prompt construction,
  history replay, answer/error sanitization, and topic summaries.
- `src/limits.ts` owns every hard limit shared by Host, Client, and tests. Changing one means
  checking `shared.ts`, `host/engine.ts`, `client/store.ts`, and the unit tests.
- `src/random.ts` must keep working on plain-HTTP origins where `crypto.randomUUID` is absent.
- `buildPrompt()` appends exactly one user-role `<btw>` prompt. It must not change the system
  prompt, the tool table, the persona, or the preset.

## Verifying

```sh
NODE=~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node
"$NODE" node_modules/vitest/vitest.mjs run
"$NODE" scripts/build.mjs
"$NODE" scripts/smoke.mjs
```

Build output is committed under `lib/`; rebuild and commit it whenever `src/` changes.
