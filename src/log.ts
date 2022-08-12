import { invoke } from "@tauri-apps/api/tauri";

enum LogLevel {
  Info = 1,
  Error = 2,
  Debug = 3,
  Trace = 4,
  Warn = 5
}

// Webview logging impementation based on:
// https://github.com/tauri-apps/tauri-plugin-log
export default class Log {
  private static async logger(level: LogLevel, message: string): Promise<void> {
    const traces = new Error().stack?.split("\n").map((line) => line.split("@"));
    const filtered = traces?.filter(([name, location]) => name.length && location !== "[native code]");
    const location = filtered?.[0]?.join("@");
    await invoke("webview_log", { level, message, location });
  }

  public static async error(msg: string): Promise<void> { await this.logger(LogLevel.Error, msg); }
  public static async debug(msg: string): Promise<void> { await this.logger(LogLevel.Debug, msg); }
  public static async trace(msg: string): Promise<void> { await this.logger(LogLevel.Trace, msg); }
  public static async warn(msg: string): Promise<void> { await this.logger(LogLevel.Warn, msg); }
  public static async info(msg: string): Promise<void> { await this.logger(LogLevel.Info, msg); }
};