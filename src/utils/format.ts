/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
import humanizeDuration from "humanize-duration";
import prettyBytes from "pretty-bytes";
import { Options } from "pretty-bytes";

const humanizer = humanizeDuration.humanizer();

humanizer.languages.shorter = {
    y: () => "y",
    mo: () => "mo",
    w: () => "w",
    d: () => "d",
    h: () => "h",
    m: () => "min",
    s: () => "sec",
    ms: () => "ms",
};

humanizer.languages.shortest = {
    y: () => "y",
    mo: () => "mo",
    w: () => "w",
    d: () => "d",
    h: () => "h",
    m: () => "m",
    s: () => "s",
    ms: () => "ms",
};

export const tryFormatEval = (str: string, data: any): string => {
    // TODO find safer alternative to eval
    return eval("`" + str.replace(/`/g, "\\`") + "`");
};

export const tryFormatArgsEval = (args: string[], data: any) => {
    return args.map((arg: string) => {
        try {
            return tryFormatEval(arg, data);
        } catch (error) {
            return arg;
        }
    });
};

export function percent(partial: number, total: number) {
    return `${Math.round((partial / total) * 100)}%`;
}

export function faIcon(cls: string, type?: string): string {
    return `<i class='${type ?? "fa"} ${cls} '></i>`;
}

export function pBytes(value: number, options?: Options): string {
    return prettyBytes(value, options);
}
