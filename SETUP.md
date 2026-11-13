# SETUP

Replicate this DeepSeek Harness setup on a fresh machine.

**If you are an AI agent: read this file only.** Do not read `README.md`, `HANDOFF.md` or `docs/` first — everything needed is here, and exploring the repository costs far more than following it. The whole job is eight commands.

## 1. Facts — do not re-derive these

| Fact | Value |
|---|---|
| Source of truth | this repository. Never hand-edit `~/.dsh/profiles/desktop`; change the repo and deploy. |
| Deploy and verify | `./bin/dsh apply` and `./bin/dsh doctor`. The CLI is `bin/dsh` → `tools/dshctl.py`, Python 3 stdlib only. |
| Profile | `desktop`, DeepSeek Harness Desktop `0.2.2-rc.1`. |
| Node, npm, pnpm | **not installed system-wide.** Use the DSH runtime: `~/.dsh/dsh-runtimes/*/dependencies/node/bin/node` and `.../dependencies/pnpm/bin/pnpm.mjs`. `python3` for the tools in `tools/`. |
| MCP rows | load **only when the profile starts**. Editing a bundle patch does nothing until DSH restarts. |
| DSH MCP client | has **no OAuth flow at all**. Cloudflare's API server therefore runs through the `mcp-remote` stdio bridge. |
| Cloudflare tokens | `~/.mcp-auth` (mode `0600`), outside this repository. Delete the directory to force a fresh login. |
| Secrets | `~/.dsh/.credentials.yaml` and environment variables. Never in this repository, never in a command line. |
| `apply` conflicts | a refusal is a design signal. Read the diff; only then `--force`. |
| Machine-local tools | `/opt/agents/tools/playwright-mcp` and `/opt/agents/tools/cloudflare-mcp-oauth`. |
| Agent workspace | `/opt/agents` (`0700`, `bin/` locked), provisioned from `agents/`. |
| Destructive actions | `/opt/agents/bin/rm` soft-deletes. The full gate lives in `~/.agents/AGENTS.md` §2. |

## 2. Steps

### 2.1 Install the app

Install DeepSeek Harness Desktop `0.2.2-rc.1`, launch it once so `~/.dsh/profiles/desktop` exists, then quit it.

### 2.2 Clone the repository

```sh
git clone https://github.com/aaxyat/my-dsh.git ~/Documents/Projects/my-dsh
cd ~/Documents/Projects/my-dsh
```

HTTPS clone needs no keys. Pushing later needs your Git credentials, which is a separate, interactive step.

### 2.3 Provision the agent workspace

```sh
python3 tools/provision_agents.py --dry-run
python3 tools/provision_agents.py
```

OK: `ls -ld /opt/agents` shows `drwx------` and `/opt/agents/bin/preflight` runs. Idempotent — safe to re-run. A conflict means the installed copy drifted from `agents/`; review the diff, then re-run with `--force`.

### 2.4 Deploy the profile

```sh
./bin/dsh apply --dry-run
./bin/dsh apply --with-plugins
```

OK: `applied: N change(s)`, zero conflicts, zero plugin failures.

If it reports conflicts, **stop**. Run `./bin/dsh apply --dry-run` and read which files differ. Only after you understand the difference, `./bin/dsh apply --force --with-plugins` (it backs up what it replaces).

`apply` also installs the third-party skill packs: it clones each pack at the commit pinned in `harness/skills/packs.json` into `/opt/agents/tools/skill-packs/`, then links the selected skills into `~/.agents/skills`. The first run needs network access; `--no-packs` skips it. Re-run just that step with `./bin/dsh skills sync`.

### 2.5 Restore credentials

Create `~/.dsh/.credentials.yaml` with mode `600` holding the API keys the profile references by name. Ask the user for the names if they are not already known — `docs/secrets.md` lists them. Nothing goes in this repository.

### 2.6 Install the machine-local MCP servers

```sh
python3 tools/provision_playwright_mcp.py --dry-run
python3 tools/provision_playwright_mcp.py
python3 tools/provision_cloudflare_mcp_oauth.py --dry-run
python3 tools/provision_cloudflare_mcp_oauth.py
```

Both are idempotent. OK: `node_modules` exists under both targets under `/opt/agents/tools/`.

### 2.7 Sign in to Cloudflare

The last command prints the login command. Run it, approve the request in the browser that opens.

OK: `Connected successfully!` and a token file appears in `~/.mcp-auth`.

Skip this step if `~/.mcp-auth` already holds a token from a previous login.

### 2.8 Restart and verify

Quit DeepSeek Harness completely and reopen it. MCP rows do not hot-reload.

```sh
./bin/dsh doctor
```

OK: profile in sync, no drift, no missing symlinks, and `./bin/dsh skills status` reports 43 linked, 0 stale, 0 missing. Then have the agent call `mcp__cloudflare__whoami` — it must return the account and user. If that tool is absent, the profile did not restart, not a code problem.

## 3. When something fails

| Symptom | Do this |
|---|---|
| `node: command not found` | Use `~/.dsh/dsh-runtimes/*/dependencies/node/bin/node`, not `node`. |
| `apply` reports conflicts | Read the diff; `--force` only after you can explain it. |
| An MCP tool is missing | Restart DSH. A patch edit alone changes nothing. |
| Cloudflare answers `401` or tools vanish | `rm -rf ~/.mcp-auth`, then step 2.7 again. |
| The bridge starts but idles | Run step 2.7 again; the token expired. |
| `check` fails after an edit | Fix the report before committing. `check` must pass with zero errors. |

## 4. Daily loop

```sh
./bin/dsh capture     # the app changed something -> pull it into the repo
./bin/dsh apply       # the repo changed -> push it to the app
./bin/dsh doctor      # are they in sync?
```

Commit, and push. `./bin/dsh check` must pass first.

## 5. Keeping this file true

Anyone who changes a setup step — a path, a command, a version, a fact in §1 — updates this file **in the same commit**. It is the entry point for a fresh machine and for an agent with a small context budget: if it drifts, every future setup pays for it in tokens.

Keep it under roughly 150 lines. Detail belongs in `README.md` and `docs/`, not here.
