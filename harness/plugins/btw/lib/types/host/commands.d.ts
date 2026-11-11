/**
 * Hidden command transport.
 *
 * The Client half reaches the Host through the existing authenticated
 * `commands.execute` RPC. This avoids opening an unauthenticated HTTP route for
 * history or answers. The trade-off — command lifecycle records include the
 * result text — is documented in the README; the public endpoints stay hidden
 * from the slash menu.
 */
import type { Context } from '@deepseek-ai/cordis';
import type { BtwEngine } from './engine';
export declare function registerBtwCommands(ctx: Context, engine: BtwEngine): Array<() => void>;
/**
 * Keep the transport commands out of the slash-command directory while leaving
 * `find`/`execute` intact for the authenticated RPC. The wrapper is removed on
 * plugin unload, and a later wrapper installed by another plugin is preserved.
 */
interface LifecycleSink {
    appendLifecycle?(session: unknown, type: string, data: {
        name?: string;
        commandId?: string;
    }): void;
}
/**
 * Keep the internal transport out of the session log as well as the slash
 * directory. `commands.execute` logs a run/done pair around every handler; for
 * Btw those pairs would add Chat nodes and copy the whole topic JSON of
 * `btw-get` into `command/done`. Suppressing that pair keeps the authenticated
 * RPC path (no new HTTP surface) without polluting the main transcript.
 *
 * This is an instance-level compatibility shim, like the directory filter. If a
 * future DSH removes `appendLifecycle`, the plugin still works and logs the
 * commands; the warning is emitted by the caller.
 */
export declare function quietInternalCommands(commands: LifecycleSink, onUnsupported?: () => void): () => void;
export declare function hideInternalCommands(commands: {
    list: (agent: unknown) => readonly {
        name: string;
    }[];
}): () => void;
export {};
