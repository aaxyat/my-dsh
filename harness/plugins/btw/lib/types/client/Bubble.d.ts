import React from 'react';
import type { BtwClientStore } from './store';
/** Rendered at `conversation.input.overlay`; floats above the composer card. */
export declare function BubbleLayer({ store, sessionId, onInsert }: {
    readonly store: BtwClientStore;
    readonly sessionId: string;
    readonly onInsert?: (text: string) => void;
}): React.JSX.Element | null;
