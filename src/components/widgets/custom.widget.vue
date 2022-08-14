<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import { invoke } from "@tauri-apps/api/tauri";
import { ref, onMounted } from "vue";
import { CallbackEvent } from "~/bindings/widget/base/CallbackEvent";
import { CallbackType } from "~/bindings/widget/base/CallbackType";
import { CallbackTypeExec } from "~/bindings/widget/base/CallbackTypeExec";
import { CustomCommandResponse } from "~/bindings/widget/custom/CustomCommandResponse";
import type { CustomWidgetProps } from "~/bindings/widget/custom/CustomWidgetProps";

const props = defineProps<CustomWidgetProps>();

// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
let data: any;
let showAltLabel = false;
let activeLabel: string;
let commandResult: CustomCommandResponse;

const defaultLabel = "CustomWidget";
const activeLabelError = ref<string | null>(null);
const activeLabelFormatted = ref<string>(
  props.label_alt ?? props.label ?? defaultLabel
);

onMounted(async () => {
  activeLabel = props.label ?? defaultLabel;

  if (props.command) {
    await executeCommand();

    if (props.command.interval ?? 0 > 0) {
      setInterval(executeCommand, props.command.interval!);
    }
  }
});

const executeCommand = async () => {
  commandResult = await invoke("process_custom_command", {
    command: props.command?.cmd,
    args: props.command?.args ?? [],
    timeout: props.command?.timeout ?? props.command?.interval ?? 1000,
    detach: props.command?.detach_process ?? true,
  });

  updateActiveLabel();
};

const updateActiveLabel = () => {
  if (commandResult.stdout) {
    try {
      data = JSON.parse(commandResult.stdout);
    } catch {
      data = commandResult.stdout.replace(/(\r\n|\n|\r)/gm, "");
    }
    try {
      const fmt = eval("`" + activeLabel.replace(/`/g, "\\`") + "`");
      activeLabelFormatted.value = fmt;
      activeLabelError.value = null;
    } catch (error) {
      activeLabelFormatted.value = "Error";
      activeLabelError.value = `Error formatting label:\n\n${
        (error as Error).message
      }`;
    }
  } else {
    const cmd = props.command?.cmd;
    const args = ` ${(props.command?.args ?? []).join(" ")}`;
    const status = commandResult.status ?? 1;

    if (commandResult.stderr) {
      activeLabelError.value = `Command: "${cmd}${args}" exited with code: ${status}\n\n${commandResult.stderr}`;
    } else {
      activeLabelError.value = `Unknown Error. Check log for details.`;
    }

    activeLabelFormatted.value = cmd ?? "error";
  }
};

const swapActiveLabel = () => {
  showAltLabel = !showAltLabel;
  activeLabel = (showAltLabel ? props.label_alt : props.label) ?? defaultLabel;
  updateActiveLabel();
};

const processCallback = async (callbackEvent: CallbackEvent) => {
  if (props.callbacks) {
    const callbackType: CallbackType | null = props.callbacks[callbackEvent];

    if (typeof callbackType === "string") {
      switch (callbackType) {
        case "toggle":
          swapActiveLabel();
          break;
        case "update":
          if (props.command) {
            await executeCommand();
          }
          break;
      }
    } else {
      if (callbackType?.exec) {
        await processExecCallback(callbackType as CallbackTypeExec);
      }
    }
  }
};

const processExecCallback = async (callback: CallbackTypeExec) => {
  const command = callback?.exec?.cmd;
  const args = callback.exec.args ?? [];

  // format any args that might be template literals
  tryFormatArgs(args);

  await invoke("process_custom_command", { command, args, timeout: 1000 });
};

const tryFormatArgs = (args: string[]) => {
  args.map((arg) => {
    try {
      return eval("`" + arg.replace(/`/g, "\\`") + "`");
    } catch (error) {
      return arg;
    }
  });
};

const mouseoutUntoggle = () => {
  if (props.callbacks?.on_hover === "toggle") {
    swapActiveLabel();
  }
};
</script>

<template>
  <span
    :data-toggle="!!activeLabelError"
    :title="activeLabelError ?? ''"
    :class="['widget', props.class, { error: !!activeLabelError }]"
    @click.left="processCallback('on_left')"
    @click.middle="processCallback('on_middle')"
    @click.right="processCallback('on_right')"
    @mouseover="processCallback('on_hover')"
    @mouseout="mouseoutUntoggle()"
  >
    {{ activeLabelFormatted }}
  </span>
</template>
