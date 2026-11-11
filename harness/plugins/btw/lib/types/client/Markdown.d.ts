import React from 'react';
/**
 * Answers are model text. Render GFM Markdown but never raw HTML, remote
 * images, or unsanitized embedded content. Links open outside the app.
 */
export declare function BtwMarkdown({ text, streaming }: {
    readonly text: string;
    readonly streaming?: boolean;
}): React.JSX.Element;
