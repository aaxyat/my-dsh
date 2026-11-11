export declare const PLUGIN_NAME = "btw";
export declare const LOCALE_NS = "btw";
/** The only user-facing command name. Internal commands are hidden. */
export declare const BTW_COMMAND = "btw";
export declare const ASK_COMMAND = "btw-ask";
export declare const LIST_COMMAND = "btw-list";
export declare const GET_COMMAND = "btw-get";
export declare const CANCEL_COMMAND = "btw-cancel";
export declare const DELETE_COMMAND = "btw-delete";
export declare const INTERNAL_COMMANDS: readonly ["btw-ask", "btw-list", "btw-get", "btw-cancel", "btw-delete"];
export type InternalCommand = (typeof INTERNAL_COMMANDS)[number];
export type BtwLocale = 'zh' | 'en';
export type BtwStatus = 'running' | 'complete' | 'cancelled' | 'error' | 'interrupted';
/** One side question and its answer. Only user-visible text is stored. */
export interface BtwTurn {
    readonly id: string;
    readonly question: string;
    readonly answer: string;
    readonly status: BtwStatus;
    readonly error?: string;
    readonly reference?: string;
    readonly createdAt: number;
    readonly updatedAt: number;
    readonly childSessionId?: string;
}
/** A topic is the follow-up line: turn[0] is its root question. */
export interface BtwTopic {
    readonly id: string;
    readonly parentSessionId: string;
    readonly title: string;
    readonly createdAt: number;
    readonly updatedAt: number;
    readonly turns: readonly BtwTurn[];
}
export interface BtwTopicSummary {
    readonly id: string;
    readonly title: string;
    readonly turnCount: number;
    readonly status: BtwStatus;
    readonly createdAt: number;
    readonly updatedAt: number;
    readonly lastQuestion: string;
}
export interface AskRequest {
    readonly turnId: string;
    readonly topicId?: string;
    readonly question: string;
    readonly reference?: string;
    readonly locale: BtwLocale;
}
export interface AskAccepted {
    readonly topic: BtwTopic;
    readonly turn: BtwTurn;
    /** Last completed parent turn inherited by the fork; side nodes start after it. */
    readonly baselineTurn: number;
}
export interface ListRequest {
    readonly limit?: number;
}
export interface ListResult {
    readonly topics: readonly BtwTopicSummary[];
}
export interface GetRequest {
    readonly topicId: string;
}
export interface GetResult {
    readonly topic: BtwTopic;
}
export interface CancelRequest {
    readonly topicId?: string;
    readonly turnId?: string;
}
export interface DeleteRequest {
    readonly topicId: string;
}
export interface DeleteResult {
    readonly deleted: true;
}
export declare function isUuid(value: unknown): value is string;
export declare function isBtwLocale(value: unknown): value is BtwLocale;
export declare class BtwRequestError extends Error {
    name: string;
}
export declare function parseAskRequest(raw: string): AskRequest;
export declare function parseListRequest(raw: string): ListRequest;
export declare function parseGetRequest(raw: string): GetRequest;
export declare function parseCancelRequest(raw: string): CancelRequest;
export declare function parseDeleteRequest(raw: string): DeleteRequest;
/** JSON command line used by the Client to reach a hidden Host command. */
export declare function commandLine(name: InternalCommand, payload: unknown): string;
export declare function titleOf(question: string): string;
export declare function summarizeTopic(topic: BtwTopic): BtwTopicSummary;
export interface OpenPromptInput {
    readonly question: string;
    readonly reference?: string;
    readonly history?: readonly BtwTurn[];
    readonly parentPartial?: string;
    readonly parentProgress?: string;
    readonly parentOpenTools?: readonly string[];
    readonly locale?: BtwLocale;
}
/**
 * Serialize previous turns as reference text. Newest turns win when the topic
 * exceeds the replay budget; a follow-up still sees the parent conversation
 * directly through the fork, so trimming stale side history is safe.
 */
export declare function formatHistory(history: readonly BtwTurn[]): string;
/**
 * Build the one user-role prompt appended after the inherited prefix.
 *
 * Nothing in this function is allowed to touch the system prompt, the tool
 * table, or an inherited message. The instructions live in the appended user
 * turn so the parent request prefix stays byte-identical.
 */
export declare function buildPrompt(input: OpenPromptInput): string;
/**
 * Models sometimes imitate the inherited tool-call vocabulary even when the
 * guard rejects it. Remove those artifacts from the visible answer; never
 * remove ordinary prose or code fences.
 */
export declare function sanitizeAnswer(raw: string): string;
export declare function sanitizeError(error: unknown): string;
export declare function truncateUtf8(text: string, maxBytes: number): string;
/** Aggressively compact a model/tool error for display. */
export declare function cleanHostError(error: unknown, fallback: string): string;
export declare const LIMITS: {
    readonly MAX_QUESTION_LENGTH: 8000;
    readonly MAX_REFERENCE_LENGTH: 8000;
    readonly MAX_HISTORY_CHARS: 64000;
    readonly MAX_ANSWER_BYTES: number;
    readonly MAX_TOPICS_PER_SESSION: 50;
    readonly MAX_TURNS_PER_TOPIC: 200;
};
