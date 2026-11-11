/**
 * btw — read-only side questions for DeepSeek Harness.
 *
 * Host half: reserve a child id, fork the current session, deny every tool at
 * execution time, persist one turn, and expose hidden authenticated commands
 * for the Web Client. The public `/btw` command is claimed by the Client input
 * source so it can render a bubble instead of a command result.
 */
import type { Context } from '@deepseek-ai/cordis';
export declare const name = "btw";
export declare const inject: string[];
export declare function apply(ctx: Context): Promise<void>;
