# @local/cloudflare-mcp — Cloudflare API and docs for DSH

A **configuration-only bundle** that inserts one `@deepseek-ai/dsh-mcp-client` row giving the agent
the whole Cloudflare API (2,500+ endpoints) plus Cloudflare's developer documentation. It ships no
Host or Client code.

## What it mounts

```yaml
serverName: cloudflare
transport: stdio
command: <DSH runtime node>
args: [/opt/agents/tools/cloudflare-mcp-oauth/node_modules/mcp-remote/dist/proxy.js,
       https://mcp.cloudflare.com/mcp]
```

The remote endpoint is `https://mcp.cloudflare.com/mcp`, reached through the **mcp-remote** stdio
bridge. It answers with four code-mode tools instead of one tool per API endpoint, so the whole API
costs roughly 1.1 K tokens of schema rather than 1.17 M:

| Tool | Purpose |
| --- | --- |
| `search` | Run JavaScript over the Cloudflare OpenAPI spec to find endpoints |
| `execute` | Run JavaScript against `cloudflare.request()` to make real API calls |
| `docs` | Search Cloudflare's developer documentation |
| `whoami` | Confirm which account and user the token belongs to |

Tool names are `mcp__cloudflare__search`, `mcp__cloudflare__execute`, `mcp__cloudflare__docs`,
`mcp__cloudflare__whoami`.

## Why a bridge

The endpoint requires OAuth — it answers `401` with
`www-authenticate: Bearer realm="OAuth", resource_metadata="…/oauth-protected-resource/mcp"`. DSH's
MCP client has no OAuth flow, no token store and no sign-in state, so a direct
`streamable-http` row fails permanently with reconnect churn.

`mcp-remote` fills that gap: it discovers the protected-resource and authorization-server metadata,
registers a client dynamically, runs authorization-code + PKCE in the browser, stores the tokens in
`~/.mcp-auth` (mode `0600`) and serves them to DSH over stdio. It also refuses to present stored
credentials to an authorization server other than the one that issued them (RFC 9207 issuer
binding).

## Install

```sh
./bin/dsh apply --with-plugins
python3 tools/provision_cloudflare_mcp_oauth.py     # installs the bridge, prints the login command
```

Then authenticate once, approving in the browser:

```sh
<User>/.dsh/dsh-runtimes/<runtime>/dependencies/node/bin/node \
  /opt/agents/tools/cloudflare-mcp-oauth/node_modules/mcp-remote/dist/client.js \
  https://mcp.cloudflare.com/mcp
```

The grant is `user:read account:read offline_access` — read-only account and zone metadata with a
refresh token, no permission to change resources.

## Verify

- `./bin/dsh doctor` reports the profile in sync.
- After restarting DSH, `plugin-manager` lists `include:mcp-cloudflare` as `active`.
- Calling `mcp__cloudflare__whoami` returns the authenticated account and user.

## Renewal

Tokens refresh silently. If the refresh token expires or is revoked, the row fails at startup;
re-run the login command above and restart DSH. To discard all local OAuth state,
`rm -rf ~/.mcp-auth`.

The bridge is a pin of `mcp-remote@0.16.6` with install scripts disabled. Its OAuth tokens are the
only secret involved; they live outside this repository and outside `/opt/agents`.
