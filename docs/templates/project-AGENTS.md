# AGENTS.md — <project name>

<!--
Template for a project-level instruction file. Place it at the project root
(the directory containing `.git`). It is loaded after user-global instructions,
so it can add project specifics but should not repeat them.
Keep it short: every line costs context in every session.
-->

## What this project is

One paragraph: purpose, stack, entry points, how it is run and tested.

## Commands

```sh
# install
# test
# lint / typecheck
# run locally
```

## Conventions

- Language/framework rules that differ from defaults.
- Formatting and lint expectations.
- Branch/commit conventions if they differ from Conventional Commits.

## Invariants

- Things that must never break (schemas, public APIs, migrations).
- Required ordering of steps.

## Gotchas

- Non-obvious failures and their fixes.
- External services that need credentials (name the variables, never the values).

## Definition of done

What must pass before a change is considered complete in this project.
