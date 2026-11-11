import { summarizeTopic, type AskAccepted, type AskRequest, type BtwTopic, type BtwTopicSummary } from '../shared';
import { type StreamCapture } from './parent-context';
import type { ChildGuard } from './tool-guard';
import type { BtwStore } from './store';
export interface ParentAgent {
    readonly id: string;
    readonly status: 'idle' | 'running';
    readonly options?: {
        readonly maxTokens?: number;
    };
    readonly session?: {
        readonly header?: {
            readonly origin?: string;
        };
        snapshotEvents?(): readonly {
            readonly type: string;
            readonly data?: unknown;
        }[];
    };
}
export interface ChildOutputBlock {
    readonly type: string;
    readonly text?: string;
}
export interface ChildResult {
    readonly stopReason: string;
    readonly output: readonly ChildOutputBlock[];
    readonly diagnostic?: string;
}
export interface ChildHandle {
    readonly result: Promise<ChildResult>;
    dispose(): Promise<void>;
}
export interface StartChildRequest {
    readonly parent: ParentAgent;
    readonly childId: string;
    readonly prompt: string;
    readonly signal: AbortSignal;
    readonly maxTokens: number;
    readonly label: string;
}
export interface BtwEngineOptions {
    readonly store: BtwStore;
    readonly startChild: (request: StartChildRequest) => Promise<ChildHandle>;
    readonly guard: ChildGuard;
    readonly capture: StreamCapture;
    readonly now?: () => number;
    readonly uuid?: () => string;
    readonly timeoutMs?: number;
    readonly cleanupTimeoutMs?: number;
    readonly archiveChild?: (childId: string) => Promise<void>;
    readonly log?: (message: string, error?: unknown) => void;
}
export interface AskInput extends AskRequest {
    readonly parent: ParentAgent;
}
export declare class BtwBusyError extends Error {
    name: string;
    constructor();
}
export declare class BtwCapacityError extends Error {
    name: string;
    constructor();
}
export declare class BtwNotFoundError extends Error {
    name: string;
    constructor();
}
export declare class BtwEngine {
    private readonly options;
    private readonly active;
    private readonly cancelledTurns;
    private readonly now;
    private readonly uuid;
    private readonly timeoutMs;
    private readonly cleanupTimeoutMs;
    private readonly log;
    private closed;
    constructor(options: BtwEngineOptions);
    get activeCount(): number;
    hasActive(parentSessionId: string): boolean;
    ask(input: AskInput): Promise<AskAccepted>;
    /** Run one child to completion and persist the canonical status. */
    private settle;
    list(parentSessionId: string, limit?: number): BtwTopicSummary[];
    get(parentSessionId: string, topicId: string): BtwTopic;
    cancel(parentSessionId: string, topicId?: string, turnId?: string): Promise<void>;
    delete(parentSessionId: string, topicId: string): Promise<boolean>;
    private pruneCancelled;
    dispose(): Promise<void>;
    private updateTurn;
    private bounded;
}
export { summarizeTopic };
