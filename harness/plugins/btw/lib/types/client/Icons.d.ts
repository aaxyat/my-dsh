import React from 'react';
interface IconProps {
    readonly size?: number;
    readonly className?: string;
}
export declare function BtwIcon({ size, className }: IconProps): React.JSX.Element;
export declare function CopyIcon(props: IconProps): React.JSX.Element;
export declare function CheckIcon(props: IconProps): React.JSX.Element;
export declare function CloseIcon(props: IconProps): React.JSX.Element;
export declare function StopIcon(props: IconProps): React.JSX.Element;
export declare function ChevronIcon({ up, ...props }: IconProps & {
    readonly up?: boolean;
}): React.JSX.Element;
export declare function HistoryIcon(props: IconProps): React.JSX.Element;
export declare function TrashIcon(props: IconProps): React.JSX.Element;
export declare function RefreshIcon(props: IconProps): React.JSX.Element;
export declare function SendIcon(props: IconProps): React.JSX.Element;
export declare function PlusIcon(props: IconProps): React.JSX.Element;
export {};
