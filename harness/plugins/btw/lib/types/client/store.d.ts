import { type BtwStatus, type BtwTopic, type BtwTopicSummary } from '../shared';
import type { TranslateFn } from './locales';
export type BubbleStatus = BtwStatus | 'starting';
export interface Bubble {
    readonly id: string;
    readonly sessionId: string;
    readonly topicId: string | null;
    readonly question: string;
    readonly reference?: string;
    readonly answer: string;
    readonly status: BubbleStatus;
    readonly error?: string;
    readonly childId?: string;
    readonly createdAt: number;
    readonly updatedAt: number;
    readonly collapsed: boolean;
    readonly streaming: boolean;
}
export interface HistoryState {
    readonly open: boolean;
    readonly sessionId: string;
    readonly topics: readonly BtwTopicSummary[];
    readonly selectedId?: string;
    readonly topic?: BtwTopic;
    readonly loading: boolean;
    readonly loadingTopic: boolean;
    readonly error?: string;
}
export interface BtwSnapshot {
    readonly bubbles: readonly Bubble[];
    readonly history: HistoryState | null;
}
export interface Bridge {
    call(sessionId: string, name: string, payload: unknown, signal?: AbortSignal): Promise<unknown>;
}
interface SessionSnapshotLike {
    readonly running?: boolean;
    readonly subagent?: unknown;
    readonly removed?: boolean;
    readonly openState?: string;
}
export interface SessionFaceLike {
    getSnapshot(): SessionSnapshotLike;
    subscribe(listener: () => void): () => void;
}
export interface SessionReferenceLike {
    readonly sessionId: string;
    readonly ready: Promise<unknown>;
    readonly binding: {
        readonly session: SessionFaceLike;
    };
    release(): void;
}
export interface SessionsLike {
    retain(id: string, options: {
        source: string;
    }): SessionReferenceLike;
    binding(id: string): {
        readonly session: SessionFaceLike;
    } | undefined;
}
interface ChatSnapshotLike {
    readonly legacy?: {
        readonly partial?: {
            readonly blocks?: readonly AssistantBlockLike[];
        } | null;
        readonly nodes?: readonly NodeLike[];
    };
    readonly nodes?: {
        values?(): readonly NodeLike[];
    };
}
interface NodeLike {
    readonly kind?: string;
    readonly turn?: number;
    readonly blocks?: readonly AssistantBlockLike[];
    readonly message?: string;
    readonly error?: string;
}
interface AssistantBlockLike {
    readonly kind?: string;
    readonly text?: string;
}
export interface ConversationLike {
    binding(binding: unknown): {
        target(name: 'chat'): {
            getSnapshot(): ChatSnapshotLike | undefined;
            subscribe(listener: () => void): () => void;
        };
    };
}
export interface StoreOptions {
    readonly bridge: Bridge;
    readonly sessions?: SessionsLike;
    readonly conversation?: ConversationLike;
    readonly t: TranslateFn;
    readonly uuid?: () => string;
    readonly now?: () => number;
    readonly source?: string;
    readonly locale?: () => 'zh' | 'en';
    readonly maxBubblesPerSession?: number;
    readonly log?: (message: string, error?: unknown) => void;
}
export declare class BtwClientStore {
    private readonly options;
    private snapshot;
    private readonly listeners;
    private readonly watchers;
    private readonly cancelled;
    private readonly pending;
    private readonly historyControllers;
    private readonly now;
    private readonly uuid;
    private readonly source;
    private readonly maxBubbles;
    private readonly log;
    private disposed;
    constructor(options: StoreOptions);
    getSnapshot: () => BtwSnapshot;
    subscribe: (listener: () => void) => (() => void);
    get t(): TranslateFn;
    canAsk(sessionId: string): string | undefined;
    /**
     * Start one side question. Validation throws synchronously so the input
     * claim can report a composer error; Host failures land in the bubble.
     */
    ask(sessionId: string, question: string, options?: {
        topicId?: string;
        reference?: string;
    }): string;
    retry(bubbleId: string): void;
    cancel(bubbleId: string): Promise<void>;
    dismiss(bubbleId: string): void;
    toggleCollapse(bubbleId: string): void;
    openHistory(sessionId: string): Promise<void>;
    closeHistory(): void;
    refreshHistory(): Promise<void>;
    selectTopic(topicId: string): Promise<void>;
    deleteTopic(topicId: string): Promise<void>;
    followUp(sessionId: string, topicId: string, question: string): string;
    /** Retry one historical turn as a fresh turn in the same topic. */
    retryTurn(sessionId: string, topicId: string, question: string): void;
    dispose(): Promise<void>;
    private runAsk;
    private watch;
    private check;
    private finalize;
    /**
     * Retaining the child can fail when the Client has not seen its catalog row
     * yet. The Host still owns the result, so read it back a few times before
     * declaring the bubble detached.
     */
    private recoverWithoutChild;
    private readChat;
    private releaseWatcher;
    private loadTopics;
    private loadTopic;
    private mergeTopic;
    private makeRoom;
    private findBubble;
    private update;
    private patchHistory;
    private publish;
}
export {};
