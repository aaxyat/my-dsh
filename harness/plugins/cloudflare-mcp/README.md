# @local/cloudflare-mcp — Cloudflare documentation for DSH

A **configuration-only bundle** that inserts a remote `@deepseek-ai/dsh-mcp-client` row for
Cloudflare's documentation MCP server. It ships no Host or Client code.

## What it mounts

```yaml
serverName: cloudflare
transport: streamable-http
url: https://docs.mcp.cloudflare.com/mcp
```

Exposes `mcp__cloudflare__search_cloudflare_documentation` and
`mcp__cloudflare__migrate_pages_to_workers_guide`.

This is the **documentation** server. It works anonymously and answers questions about Cloudflare
products; it does not read or change account resources.

## Account API access

Cloudflare's account-wide API server is `https://mcp.cloudflare.com/mcp`. It requires OAuth
(`search`, `execute`, `docs`, `whoami` tools). DSH's MCP client has no browser OAuth flow, so this
bundle deliberately mounts the docs server instead. To use the API server, add a row with an
`Authorization: Bearer …` API token stored outside this repository, or wait for DSH MCP OAuth
support.

## Install

```sh
./bin/dsh apply --with-plugins
```

The bundle is linked into the `desktop` profile and selected in `dsh.profile.bundles`.

## Verify

- `plugin-manager` lists `include:mcp-cloudflare` as `active`.
- A `search_cloudflare_documentation` query for "Workers KV binding configuration" returns
  `developers.cloudflare.com` pages.
