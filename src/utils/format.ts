/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
import humanizeDuration from "humanize-duration";
import prettyBytes from "pretty-bytes";
import moment from "moment";

const humanizer = humanizeDuration.humanizer();
const pb = prettyBytes;
const m = moment;

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

export function percentage(partial: number, total: number) {
  return `${Math.round((partial / total) * 100)}%`;
}
