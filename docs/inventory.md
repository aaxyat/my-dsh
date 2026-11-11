# Inventory — `machine/inventory.json`

A point-in-time snapshot of the machine that produced this repository. It is **generated** by `./bin/dsh capture`; do not hand-edit it.

Its purpose is provenance and drift detection: given a report from another machine, you can tell which DSH version, runtime, profile, bundles, skills and credential *names* were in play.

## Current snapshot

| Field | Value |
|---|---|
| Captured | 2026-11-11 (UTC) |
| Host | Mac16,1 · arm64 · Darwin 27.0.0 |
| DSH desktop | `0.2.2-rc.1` |
| Profile | `desktop` |
| Runtime | node `24.21.0` · pnpm `11.28.5` · python `3.12.14` |
| Bundles | `dsh-base`, `dsh-web-app`, `@local/pinned-workspaces` |
| Profile dependencies | 1 (`@local/pinned-workspaces`, linked from `harness/plugins/`) |
| Personal skills | 0 |
| Bundled skills | 12 |
| User-global instructions | `AGENTS.md` + `RULES.md`, deployed as symlinks |
| Agent workspace | `/opt/agents` · 10 helpers · `bin/` locked |
| Credential refs (names only) | `DEEPSEEK_API_KEY`, `OPENCODE_GO_API_KEY` |
| Managed files recorded | 5 |

Bundled skills visible to the model on this install: `agent-experience`, `cordis-composition-reference`, `cordis-plugin-development`, `diagnose-windows-sandbox-acl`, `editing-cordis-compositions`, `office`, `office-docx`, `office-export-pdf`, `office-pptx`, `office-recalculate`, `office-render`, `office-xlsx`.

## Schema

| Key | Meaning |
|---|---|
| `schema` | Inventory format version (currently `1`). |
| `generatedBy` | The command that wrote the file. |
| `capturedAt` | UTC timestamp. |
| `host` | OS, kernel release, architecture, Apple model identifier, Python version. No hostname or username. |
| `dsh` | Installed desktop version, active profile, home paths, app path. |
| `runtime` | Node/pnpm/Python versions from the DSH runtime manifest. |
| `profile.bundles` | Ordered `dsh.profile.bundles` — later entries win. |
| `profile.dependencies` | Profile npm dependencies (third-party and personal links). |
| `plugins` | Installed dependencies, third-party list, and each personal plugin's install/enable/deploy state. |
| `skills` | Personal skill names, bundled skill names, user skill root. |
| `instructions` | List of instruction artifacts: repo source, deploy target, and whether each was linked at capture time. |
| `agentWorkspace` | Source tree, target path, installed helpers, provisioning timestamp and source commit. |
| `credentials` | Credential store path and **names only**. Values are never read into the file. |
| `managedFiles` | SHA-256 and byte size for every deployed source file (profile files, global instructions, skill files). |

## How `check` uses it

`./bin/dsh check` compares the current hashes of copied profile files with `managedFiles`:

- match → the repo reflects the last capture;
- mismatch → a warning telling you to run `./bin/dsh capture`.

This is why CI can warn (not fail) when a profile edit has not been captured yet. The hash is over the repository file, not the live file; deployment drift is `doctor`'s job.

## Privacy

- Only the **names** of credential references are recorded.
- The network hostname and user name are deliberately omitted; the Apple model identifier is enough to explain environment-specific behaviour.
- `profile.dependencies` contains absolute `link:` paths for personal plugins because pnpm requires an absolute target. On another machine, `./bin/dsh apply --with-plugins` rewrites them to that machine's repository path. This is recorded as a known portability wrinkle in [HANDOFF](../HANDOFF.md#known-gaps).

## Refreshing

```sh
./bin/dsh capture
git diff machine/inventory.json
```

Recapture after: a DSH upgrade, plugin install/removal, skill deployment, credential reference change, or restore on a new machine. Commit the diff with the change that caused it.
