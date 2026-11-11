# @local/parallel-mcp — Parallel web search for DSH

A **configuration-only bundle**: it ships no Host or Client code. Its patch inserts one
`@deepseek-ai/dsh-mcp-client` row, so DSH exposes Parallel's tools to the agent as
`mcp__parallel-mcp__<tool>`.

## What it mounts

```yaml
serverName: parallel-mcp
transport: streamable-http
url: https://mcp.parallel.ai/mcp
failOnStartupError: true
```

This is the **anonymous** endpoint. It exposes `web_search`, `web_fetch`, `web_decisions` and the
extra search utilities; `web_research` is unavailable without browser sign-in. Anonymous use has
lower rate limits. To sign in, change the URL to
`https://mcp.parallel.ai/mcp?login`, reinstall the bundle, and complete the browser flow.

## Install

```sh
./bin/dsh apply --with-plugins
```

The bundle is `link:` installed into the `desktop` profile and selected in
`dsh.profile.bundles`. DSH starts it at boot; no build step is needed.

## Why a bundle instead of a profile-patch row

A normal MCP server is one row in `harness/profile/desktop/cordis.patch.yml`. That row works at
startup, but the running desktop app does not hot-add a new profile-patch row. A configuration-only
bundle is installed through the plugin manager, which applies it live, and it survives a restart.
The human inventory for the server is still [harness/mcp/servers.yaml](../../mcp/servers.yaml).

## Verify

```sh
# after install, ask the agent to call:
#   mcp__parallel-mcp__web_search
```

The plugin manager should list `include:mcp-parallel` as `active`, and the tool catalog should
include `mcp__parallel-mcp__web_search`.

## Data and credentials

No headers, keys or tokens are stored. Parallel provides anonymous access at the endpoint above;
a sign-in uses the provider's browser flow, not a credential in this repository.
