# @local/context7-mcp — current library documentation for DSH

A **configuration-only bundle** that inserts a remote `@deepseek-ai/dsh-mcp-client` row for
Context7. It ships no Host or Client code.

## What it mounts

```yaml
serverName: context7
transport: streamable-http
url: https://mcp.context7.com/mcp
```

Exposes `mcp__context7__resolve-library-id` and `mcp__context7__query-docs`.

## Authentication

The endpoint is used anonymously, with Context7's lower rate limits. An API key is optional and
can be added later as an `Authorization: Bearer …` header; store the key in the DSH credential
store or the environment, never in this repository. The OAuth endpoint
`https://mcp.context7.com/mcp/oauth` is not used because DSH has no MCP OAuth flow.

## Install

```sh
./bin/dsh apply --with-plugins
```

The bundle is linked into the `desktop` profile and selected in `dsh.profile.bundles`.

## Verify

- `plugin-manager` lists `include:mcp-context7` as `active`.
- Calling `mcp__context7__resolve-library-id` for `React` returns `/reactjs/react.dev` among the
  candidates.
