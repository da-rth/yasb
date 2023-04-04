/* eslint-disable @typescript-eslint/ban-ts-comment */
import * as formatters from "./format";

/**
 * Implements a safer (but *still unsafe*) eval with a limited scope given a provided context.
 * See: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval
 * @param statement The statement to be evaluated.
 * @param ctx The context to be provided within the scope of the evaluation.
 * @param allowFormatters Should formatting helper functions be added to the evaluation scope?
 * @returns The successfully evaluated value, if any (an exception is be raised on error).
 */
export const scopedEval = (statement: any, ctx: any, allowFormatters = true): any => {
    const scope: any = allowFormatters ? { ...ctx, ...formatters } : ctx;
    // @ts-ignore
    for (property in this) mask[property] = undefined;
    return new Function(`with(this) { return ${statement}; }`).call(scope);
};

/**
 * Attempts to format a given string using the provided context.
 * @param formatStr The string to be formatted e.g. "val: ${data.value}".
 * @param ctx The context to be provided when formatting the given string e.g. ctx: {data: {value: 123}}.
 * @returns The successfully formatted string (an exception is be raised on error).
 */
export const tryFormatEval = (formatStr: string, ctx: any): string => {
    return scopedEval("`" + formatStr.replace(/`/g, "\\`") + "`", ctx);
};

/**
 * Attempts to format a given array of arguments using the provided context.
 * @param formatStr The array of string arguments to be formatted.
 * @param ctx The context to be provided when formatting the given string/
 * @returns An array of successfully formatted strings (an exception is be raised on error).
 */
export const tryFormatArgsEval = (formatArgs: string[], data: any) => {
    return formatArgs.map((arg: string) => {
        try {
            return tryFormatEval(arg, data);
        } catch (error) {
            return arg;
        }
    });
};
