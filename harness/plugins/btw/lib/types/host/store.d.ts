import type { DomainSpec } from '@deepseek-ai/dsh-storage-domain';
import type { BtwTopic, BtwTopicSummary } from '../shared';
export declare const btwDomainSpec: DomainSpec;
export declare function topicKey(parentSessionId: string, topicId: string): string;
interface StoreOptions {
    readonly now?: () => number;
    readonly onWarning?: (message: string, error?: unknown) => void;
}
/** One durable topic per side-question thread, keyed by parent session + topic. */
export declare class BtwStore {
    private readonly domain;
    readonly mode: 'storage' | 'memory';
    private readonly chains;
    private closed;
    private readonly now;
    private readonly onWarning;
    private constructor();
    static open(ctx: {
        get(name: string): unknown;
        logger?: {
            warn(message: string, ...rest: unknown[]): void;
        };
    }, options?: StoreOptions): Promise<BtwStore>;
    private static memory;
    get size(): number;
    get(parentSessionId: string, topicId: string): BtwTopic | undefined;
    list(parentSessionId: string, limit?: number): BtwTopicSummary[];
    put(topic: BtwTopic): Promise<void>;
    delete(parentSessionId: string, topicId: string): Promise<boolean>;
    /**
     * A process restart cannot resume a detached fork whose parent turn has moved
     * on. `running` is therefore a crash artifact, not work to retry; mark it
     * interrupted and never auto-send.
     */
    markInterrupted(): Promise<number>;
    close(): Promise<void>;
    private get table();
    private assertOpen;
    private enqueue;
}
export {};
