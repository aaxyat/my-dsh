# scripts/ — build and built-artifact smoke

Two Node ESM scripts, not part of the TypeScript program.

- `build.mjs` writes `lib/index.js` (Host, ESM, bundled `zod`), `lib/client.js` (Client, CJS,
  `window.__ModuleLoader__.load({id:"@local/btw", ...})`, React external), and `lib/types/`.
  Do not hand-edit `lib/`; run the build and commit its output.
- `smoke.mjs` loads the built Host bundle, loads the built Client bundle through the real module
  loader shape, runs its `apply()` with fakes, and claims `/btw` under a simulated plain-HTTP
  origin without `crypto.randomUUID`.

Run with the DSH runtime Node:

```sh
NODE=~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node
"$NODE" scripts/build.mjs
"$NODE" scripts/smoke.mjs
```

Do not import `src/` directly from smoke; it verifies `lib/`.
