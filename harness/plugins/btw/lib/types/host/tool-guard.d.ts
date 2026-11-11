/**
 * Execution-time read-only guard.
 *
 * The child fork inherits the parent's tool catalog so the provider-side
 * request prefix stays identical. A prompt alone cannot make that safe: the
 * model can still emit a tool call. This guard is monotonic and denies every
 * tool for the exact child ids this plugin reserved. It never filters the
 * catalog and never changes the system prompt.
 */
export declare const BTW_TOOL_DENIED = "Btw side questions are read-only: tool execution is disabled for this turn. Answer in text only.";
interface GuardAgent {
    readonly id?: string;
    readonly ctx?: {
        readonly tools?: {
            guard(guard: (execution: {
                readonly agent?: {
                    readonly id?: string;
                };
            }) => string | undefined): () => void | Promise<void>;
        };
    };
}
type Disposer = () => void | Promise<void>;
export declare class ChildGuard {
    private readonly owned;
    private readonly childGuards;
    readonly check: (execution: {
        readonly agent?: {
            readonly id?: string;
        };
    }) => string | undefined;
    has(id: string): boolean;
    /** Reserve the child id before the activation exists. */
    own(id: string): Disposer;
    /** Defence in depth: the child's own scope also carries the same guard. */
    attach(agent: GuardAgent): void;
    release(id: string): Promise<void>;
    releaseAll(): Promise<void>;
}
export {};
