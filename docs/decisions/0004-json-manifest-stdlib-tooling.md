# ADR-0004 — JSON manifest and stdlib-only tooling

- **Status:** Accepted
- **Date:** 2026-11-11
- **Deciders:** Ayush Bhattarai

## Context

Deployment needs a machine-readable inventory, and the tooling must run:

- on a freshly installed Mac with no Homebrew packages;
- in GitHub Actions on a bare Ubuntu runner;
- without installing Python dependencies (PyYAML, ruamel, etc.).

DSH's own configuration is YAML, and YAML would be the natural human format for a manifest. But parsing "YAML enough" without a library is error-prone, and adding a dependency contradicts the portability goal.

## Decision

- `harness/manifest.json` — JSON, parsed with the Python standard library.
- `machine/inventory.json` — JSON, generated.
- Human-facing inventory files (`harness/plugins/registry.yaml`, `harness/mcp/servers.yaml`) stay YAML because they mirror DSH-native shapes and are not parsed by tooling.
- Tooling is Python 3 stdlib only, behind a POSIX `sh` wrapper (`bin/dsh`) that locates a working interpreter (DSH's bundled Python first, then `python3`).

## Consequences

- Zero install step; `check` works anywhere Python 3 exists, including CI.
- The manifest is slightly noisier for humans than YAML; the docs explain each field and `check` validates it.
- If a future need requires real YAML parsing, add it as an explicit, documented dependency or migrate the manifest to TOML (`tomllib` is stdlib from Python 3.11), rather than half-supporting YAML.
