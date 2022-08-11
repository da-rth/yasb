<script setup lang="ts">
import { invoke } from "@tauri-apps/api/tauri";
import { ref, onMounted } from "vue"


type CustomWidgetProps = {
  kind: string,
  label: string
  label_alt?: string
  command?: CommandOptions,
  callbacks?: {
    on_left?: string | ExecCallback,
    on_middle?: string | ExecCallback,
    on_right?: string | ExecCallback,
    on_hover?: string | ExecCallback
  }
}

type CustomCommandResult = {
  stdout?: string,
  stderr?: string,
  status?: number
}

type CommandOptions = {
  cmd: string,
  args?: string[],
  interval?: number
}

type ExecCallback = {
  exec: {
    cmd: string,
    args?: string[] 
  }
}

const props = defineProps<CustomWidgetProps>();

let data;
let showAltLabel = false;
let activeLabel: string = props.label;
let activeLabelFormatted = ref<string>(props.label_alt ?? props.label);
let activeLabelError = ref<string | null>(null);
let commandResult: CustomCommandResult;

onMounted(async () => {
  if (props.command) {
    await executeCommand();

    if (props.command.interval ?? 0 > 0) {      
      setInterval(executeCommand, props.command?.interval);
    }
  }
})

let executeCommand = async () => {
  commandResult = await invoke('process_custom_command', {
    command: props.command?.cmd,
    args: props.command?.args ?? [],
    timeout: Math.floor((props.command?.interval ?? 1000) / 2)
  });

  updateActiveLabel();
}

let updateActiveLabel = () => {
  if (commandResult.stdout) {
    try {
      data = JSON.parse(commandResult.stdout);
    } catch {
      data = commandResult.stdout.replace('\n', '\\n');
    }
    try {
      let fmt = eval('`'+activeLabel.replace(/`/g,'\\`')+'`');
      activeLabelFormatted.value = fmt;
      activeLabelError.value = null;
    } catch (error) {
      activeLabelFormatted.value = "Error";
      activeLabelError.value = `Error formatting label:\n\n${(error as Error).message}`;
    }
  } else {
    let cmd = props.command?.cmd;
    let args = ` ${(props.command?.args ?? []).join(" ")}`;
    let status = commandResult.status ?? 1;

    if (commandResult.stderr) {
      activeLabelError.value = `Command: \"${cmd}${args}\" exited with code: ${status}\n\n${commandResult.stderr}`;
    } else {
      activeLabelError.value = `Unknown Error. Check log for details.`;
    }

    activeLabelFormatted.value = cmd ?? 'error';
  }
}

let swapActiveLabel = () => {
  showAltLabel = !showAltLabel;
  activeLabel = (showAltLabel ? props.label_alt : props.label) ?? props.label;
  updateActiveLabel();
}

let process_callback = async (callback_type: string) => {
  if (props.callbacks && callback_type in props.callbacks) {
    let callback = props.callbacks[callback_type as keyof typeof props.callbacks];

    if (typeof callback === "string") {
      switch (callback) {
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
      if (callback?.exec) {
        await process_exec_callback(callback);
      }
    }
  }
}

let process_exec_callback = async (callback: ExecCallback) => {
  let command = callback.exec.cmd;
  let args = callback.exec.args ?? []

  // format any args that might be template literals
  args = args.map(arg => {
    try {
      return eval('`'+arg.replace(/`/g,'\\`')+'`');
    } catch (error) {
      return arg;
    }
  });

  await invoke('process_custom_command', { command, args, timeout: 1000 });
}

let mouseout_untoggle = () => {
  if (props.callbacks?.on_hover === "toggle") {
    swapActiveLabel();
  }
}
</script>

<template>
  <span
    :data-toggle="!!activeLabelError"
    :title="activeLabelError ?? ''"
    :class="{error: !!activeLabelError}"
    @click.left="process_callback('on_left')"
    @click.middle="process_callback('on_middle')"
    @click.right="process_callback('on_right')"
    @mouseover="process_callback('on_hover')"
    @mouseout="mouseout_untoggle()"
  >
    {{ activeLabelFormatted }}
  </span>
</template>
