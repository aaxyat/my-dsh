---
name: example-skill
description: One sentence describing what this skill does and when to use it.
whenToUse: Optional. A concrete trigger, e.g. "When the user asks to convert a document to PDF."
---

# Example skill

<!--
Delete this block after copying to harness/skills/<name>/SKILL.md.

Rules:
- `name` must be kebab-case and should match the directory name.
- `description` is what the model sees in the catalog: make it specific.
- Keep this file under ~8 KB; move bulk material into references/.
- Write instructions, not prose about the topic. Assume the model is competent.
-->

## When to use

State the trigger and the non-triggers. One short paragraph.

## Procedure

1. Confirm the inputs you need (paths, formats, constraints).
2. Perform the steps in order. Include exact commands where they matter.
3. Validate the output before reporting success.

## Commands

```sh
# Prefer commands that are already available in the environment.
# Explain any required tool and how to check for it.
```

## Validation

- What "correct" looks like.
- How to verify it mechanically (command, checksum, parse, render).
- What to do when verification fails.

## References

- `references/` — optional detail loaded only when needed.
- `scripts/` — optional deterministic helpers; document each one.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| | | |
