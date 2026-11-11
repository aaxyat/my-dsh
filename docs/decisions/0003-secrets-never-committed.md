# ADR-0003 — Secrets never enter the repository

- **Status:** Accepted
- **Date:** 2026-11-11
- **Deciders:** Ayush Bhattarai

## Context

The repository is **public** and must stay useful as a restore artifact. DSH stores credentials in `~/.dsh/.credentials.yaml`; profile rows reference them by environment-variable name. Conversations, workspace indexes and caches also contain sensitive material.

A configuration backup is tempting to make "complete" by including credentials. That would make the repository a public key store, and Git history makes removal expensive.

## Decision

1. Never commit credentials, tokens, private keys, `.env` values, sessions or caches.
2. Reference credentials only by name (`apiKeyEnv: OPENCODE_GO_API_KEY`).
3. Whitelist what `capture` may copy: the three profile files plus derived inventory.
4. Keep the live credential file out of `machine/`; inventory records only the **names** it contains.
5. Enforce with `.gitignore`, a pattern scan in `./bin/dsh check`, and CI.

## Consequences

- Restoring a machine requires re-entering credentials — an accepted, documented manual step.
- The repo is safe to publish and clone anywhere.
- A leaked secret is treated as compromised immediately: revoke, then clean history (see `docs/secrets.md`).
- Scanner rules need maintenance as new key formats appear; the policy, not the scanner, is the guarantee.
