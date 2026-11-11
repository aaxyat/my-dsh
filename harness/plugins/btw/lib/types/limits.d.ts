/**
 * Shared limits. These are deliberately generous but bounded: a side question
 * inherits the whole parent context, so an unbounded answer or replayed topic
 * would grow every later request without the user seeing it.
 */
export declare const MAX_QUESTION_LENGTH = 8000;
export declare const MAX_REFERENCE_LENGTH = 8000;
export declare const MAX_HISTORY_CHARS = 64000;
export declare const MAX_ANSWER_BYTES: number;
export declare const MAX_ERROR_CHARS = 400;
export declare const MAX_TITLE_CHARS = 80;
export declare const MAX_PARENT_PARTIAL_CHARS = 8000;
/** Compact snapshot of the parent's still-open turn; this is new prompt text. */
export declare const MAX_PARENT_PROGRESS_CHARS = 6000;
export declare const MAX_TOPICS_PER_SESSION = 50;
export declare const MAX_TURNS_PER_TOPIC = 200;
export declare const MAX_ACTIVE_BTW = 4;
export declare const MAX_PROMPT_BYTES: number;
/** Hard ceiling for one detached side-question turn (10 minutes). */
export declare const DEFAULT_TIMEOUT_MS: number;
/** Cleanup must not hang the host teardown path. */
export declare const CLEANUP_TIMEOUT_MS = 5000;
/** Side answers do not need the parent turn's full completion budget. */
export declare const MAX_SIDE_OUTPUT_TOKENS = 32000;
