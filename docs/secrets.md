# Secrets — policy and incident response

This repository is **public**. Everything committed is permanent, indexed and mirrored. Treat every secret as compromised the moment it lands here.

## The contract

| Secret | Lives in | Never |
|---|---|---|
| Provider API keys (`OPENCODE_GO_API_KEY`, `DEEPSEEK_API_KEY`, …) | `~/.dsh/.credentials.yaml` (0600) or the environment that launches DSH | profile patch, skills, plugins, inventory, docs, commit messages |
| OAuth tokens / account sessions | DSH credential store | repo |
| GitHub tokens | `gh` keychain or Git credential helper | repo, scripts, `.env.example` |
| Conversation content | `~/.dsh/sessions/` | repo |
| `.env` files with values | local only | repo |

Configuration may reference a secret **by name**:

```yaml
- id: llm-pi-ai
  config:
    providers:
      opencode-go:
        apiKeyEnv: OPENCODE_GO_API_KEY   # name only — correct
```

## Defenses in this repo

1. `.gitignore` blocks `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, `**/credentials*`, `*.local.md`, `**/secrets/`.
2. `./bin/dsh check` scans every tracked text file for high-signal patterns: `sk-…`, `ghp_…`, `gho_…`, `github_pat_…`, `AKIA…`, private-key headers, and literal values assigned to `apiKey`/`token`/`secret`/`password`.
3. `capture` copies only the three whitelisted profile files — never `.credentials.yaml`, sessions or storages.
4. `machine/inventory.json` records credential **names** only.
5. CI runs `check` on every push, so a leak is at least visible before merge.

These are guardrails, not guarantees. Review `git diff` before every commit; scanners miss unfamiliar formats.

## Before you commit

```sh
./bin/dsh check
git diff --cached          # read the actual lines
git grep -nE 'sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----'
```

If a diff includes anything that looks like a credential, stop and report it rather than committing.

## If a secret is committed

Order matters: **revoke first, clean second.**

1. **Revoke/rotate** the credential at the provider. Assume the old value is public immediately.
2. Remove it from the working tree and replace it with an environment reference.
3. If it was pushed, rewrite history (`git filter-repo --path <file> --invert-paths` or `--replace-text`), then force-push **only after explicit user approval** (see `AGENTS.md` §9).
4. Tell GitHub Support if the repository has forks or is indexed; rewrite does not reach clones or caches.
5. Record the incident and rotation in `HANDOFF.md` and `CHANGELOG.md` under **Security** — without repeating the value.
6. Audit other places it may exist: shell history, logs, CI artifacts, `machine/inventory.json`, old commits in other branches/tags.

Rotating is cheap; assuming privacy after a public leak is not.

## Restoring credentials on a new machine

Never copy `~/.dsh/.credentials.yaml` between machines. Re-enter keys through DSH Settings → Account, or export them in the environment that launches DSH. See [restore.md](restore.md#4-restore-credentials).

## Why the repository is public

It is a personal portability repository, not a product. Public means no collaborator setup and easy cloning on a new machine. The tradeoff is that every commit is permanent and indexable, which is why the secret policy is strict and the capture whitelist is narrow. To revisit, see `HANDOFF.md` open questions.
