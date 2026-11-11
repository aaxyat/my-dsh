type Frame = {
    readonly type: 'start';
} | {
    readonly type: 'chunk';
    readonly chunk: {
        readonly type: string;
        readonly text?: string;
    };
} | {
    readonly type: 'end';
};
interface EventLike {
    readonly type: string;
    readonly data?: unknown;
}
export declare class StreamCapture {
    private readonly text;
    private readonly order;
    observe(sessionId: string, frame: Frame): void;
    partialOf(sessionId: string): string | undefined;
    clear(sessionId: string): void;
    private touch;
}
/**
 * Names of tool calls that have started but not settled in the parent log.
 * The fork cannot execute them and the side question must not either; the
 * prompt mentions them so the model knows they are still in flight.
 */
export declare function lastCompletedTurn(session: {
    snapshotEvents?(): readonly EventLike[];
} | undefined): number;
export declare function openToolNames(session: {
    snapshotEvents?(): readonly EventLike[];
} | undefined, limit?: number): string[];
/**
 * A compact, deterministic snapshot of the parent's open turn. The fork seed
 * ends at the last turn/end, so this is the only place the first-turn task and
 * in-flight tool work can enter the side prompt.
 *
 * This intentionally contains no completed turns (the fork already has them),
 * no timestamps, and no random ids: the snapshot is reference text, not a
 * second transcript. Callers still pass the live assistant partial separately
 * so the newest streamed text is not duplicated here.
 */
export declare function openTurnSnapshot(session: {
    snapshotEvents?(): readonly EventLike[];
} | undefined, maxChars?: number): string | undefined;
export {};
