/**
 * `/btw` as an input-trigger source rather than a monkey-patched command UI.
 *
 * The source contributes one slash candidate, claims arg-tolerant input, and
 * routes submission into the client store. The Host command with the same name
 * is deliberately not registered, so there is no catalog collision.
 */
import type { InputTriggerSource } from '@deepseek-ai/dsh-client-ui-input-trigger/client';
import type { BtwClientStore } from './store';
import type { TranslateFn } from './locales';
export interface TriggerSourceOptions {
    readonly store: BtwClientStore;
    readonly t: TranslateFn;
}
export declare const TRIGGER_SOURCE = "btw";
export declare function createBtwTriggerSource({ store, t }: TriggerSourceOptions): InputTriggerSource;
