# src/client/ — Web Client half

`index.tsx` wires the locale, the `remote.commands` bridge, the client store, the `/btw` input
trigger, and three slots. No main-transcript writes happen here.

## Slots and ids

| Slot | Component | Id | Order |
| --- | --- | --- | --- |
| `conversation.input.overlay` | `BubbleLayer` | `dsh-btw-bubbles` | 25 |
| `conversation.input.left` | `HistoryButton` | `dsh-btw-history-button` | 40 |
| `shell.overlay` | `HistoryOverlay` | `dsh-btw-history` | 30 |

The five internal command names also register `null` renderers in
`conversation.chat.commandview` so a hidden transport command cannot draw a Chat row.

## Invariants

- `/btw` is an **input trigger source**, not a monkey-patched command UI. The Host does not register
  a public `/btw` command; the Client claims the line and calls the hidden `btw-ask` command.
- Empty `/btw` opens history; text starts a side question; attachments are refused with an error
  so the draft is not silently lost.
- `store.canAsk()` refuses subagent views.
- Streaming follows the retained child session. The fork inherits the parent's completed turns, so
  nodes with `turn <= baselineTurn` must be filtered out of the bubble.
- Cancellation keeps the partial answer; closing a running bubble cancels first.
- **Insert into composer** calls `inputActions.setDraft(text)`. Never fabricate a transcript
  message or a branch.
- Markdown is rendered with `skipHtml`, images removed, and links forced to
  `target=_blank rel="noreferrer noopener"`.
- Keep the `data-testid="btw-*"` hooks and their `data-status` semantics; the smoke test and future
  browser tests use them.

## Files

`store.ts` (state machine and child retention), `trigger.ts` (slash claim), `Bubble.tsx`,
`HistoryOverlay.tsx`, `Markdown.tsx`, `Icons.tsx`, `styles.ts` (all `mgl-*` CSS), `locales.ts`.
