# locale/ — plugin-manager display metadata

`en.json` and `zh.json` feed the DSH bundle/plugin manager display only (title and one-line
description). They are not runtime UI copy; runtime strings live in `src/client/locales.ts`.

Keep both files structurally identical, valid JSON, and free of secrets, paths, and version numbers.
