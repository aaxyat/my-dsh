# @local/playwright-mcp — Playwright browser automation for DSH

A **configuration-only bundle** that inserts a stdio `@deepseek-ai/dsh-mcp-client` row for
Playwright MCP. It ships no Host or Client code.

## What it mounts

```yaml
serverName: playwright
transport: stdio
command: ~/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node
args: [/opt/agents/tools/playwright-mcp/node_modules/@playwright/mcp/cli.js,
       --headless, --browser, chromium, --isolated]
cwd: /opt/agents/tools/playwright-mcp
env: { PLAYWRIGHT_BROWSERS_PATH: /opt/agents/tools/playwright-mcp/.browsers }
```

Exposes the core browser tools (`browser_navigate`, `browser_snapshot`, `browser_click`,
`browser_type`, `browser_take_screenshot`, …) as `mcp__playwright__*`.

## Prerequisite

The server is a machine-local tool, not an npm bundle dependency. Provision it with:

```sh
./tools/provision_playwright_mcp.py
```

That installs `@playwright/mcp@0.0.85` under `/opt/agents/tools/playwright-mcp` with the DSH
runtime Node/pnpm and downloads Playwright's Chromium into the same directory. The script is
idempotent.

## Install

```sh
./bin/dsh apply --with-plugins
```

The bundle is linked into the `desktop` profile and selected in `dsh.profile.bundles`. The
plugin manager applies it live without a restart.

## Verify

- `plugin-manager` lists `include:mcp-playwright` as `active`.
- The tool catalog contains `mcp__playwright__browser_navigate`.
- Navigate to `https://example.com`; a snapshot and `Example Domain` title return.

## Caveats

- The row contains **machine-specific absolute paths** for the DSH runtime Node and the
  `/opt/agents` tool directory. Re-run the provision script and adjust the patch if the runtime
  path or workspace changes.
- Chromium is downloaded separately from the npm package; the browser directory is ~584 MB.
- `--isolated` uses a fresh browser profile for each server start, so logins do not persist.
  Remove `--isolated` to use Playwright's persistent profile.
- The server runs headless (`--headless`) and is not exposed over HTTP.
