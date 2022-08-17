/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
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
