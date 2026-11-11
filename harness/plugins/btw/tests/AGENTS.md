# tests/ — Vitest unit and wiring tests

Node-environment Vitest tests only. They do not start a Host, call a real model, or read the user's
profile.

Covered: protocol parsing and prompt construction, command hiding/lifecycle quieting, host wiring,
store behavior, engine lifecycle, tool guard, parent context, client store, trigger claim, client
apply/slot registration, and insecure-origin UUID fallback.

```sh
NODE=~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node
"$NODE" node_modules/vitest/vitest.mjs run
```

On macOS the DSH runtime Node is hardened and refuses ad-hoc native modules from npm (Rollup). If
Vitest fails with `ERR_DLOPEN_FAILED`, copy the runtime Node to scratch, re-sign the copy with
`codesign --force --sign - <copy>`, and run Vitest with that copy. The plugin itself has no native
dependencies and its built bundles load under the runtime Node.
