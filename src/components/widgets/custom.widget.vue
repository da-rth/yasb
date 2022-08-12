<script setup lang="ts">

import {invoke} from '@tauri-apps/api/tauri';
import {ref, onMounted} from 'vue';

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

let data: any;
let showAltLabel = false;
let activeLabel: string;
const activeLabelFormatted = ref<string>(props.label_alt ?? props.label);
const activeLabelError = ref<string | null>(null);
let commandResult: CustomCommandResult;

onMounted(async () => {
  activeLabel = props.label;

  if (props.command) {
    await executeCommand();

    if (props.command.interval ?? 0 > 0) {
      setInterval(executeCommand, props.command?.interval);
    }
  }
});

const executeCommand = async () => {
  commandResult = await invoke('process_custom_command', {
    command: props.command?.cmd,
    args: props.command?.args ?? [],
    timeout: Math.floor((props.command?.interval ?? 1000) / 2),
  });

  updateActiveLabel();
};

const updateActiveLabel = () => {
  if (commandResult.stdout) {
    try {
      data = JSON.parse(commandResult.stdout);
    } catch {
      data = commandResult.stdout.replace('\n', '\\n');
    }
    try {
      const fmt = eval('`'+activeLabel.replace(/`/g, '\\`')+'`');
      activeLabelFormatted.value = fmt;
      activeLabelError.value = null;
    } catch (error) {
      activeLabelFormatted.value = 'Error';
      activeLabelError.value = `Error formatting label:\n\n${(error as Error).message}`;
    }
  } else {
    const cmd = props.command?.cmd;
    const args = ` ${(props.command?.args ?? []).join(' ')}`;
    const status = commandResult.status ?? 1;

    if (commandResult.stderr) {
      activeLabelError.value = `Command: \"${cmd}${args}\" exited with code: ${status}\n\n${commandResult.stderr}`;
    } else {
      activeLabelError.value = `Unknown Error. Check log for details.`;
    }

    activeLabelFormatted.value = cmd ?? 'error';
  }
};

const swapActiveLabel = () => {
  showAltLabel = !showAltLabel;
  activeLabel = (showAltLabel ? props.label_alt : props.label) ?? props.label;
  updateActiveLabel();
};

const processCallback = async (callbackType: string) => {
  if (props.callbacks && callbackType in props.callbacks) {
    const callback = props.callbacks[callbackType as keyof typeof props.callbacks];

    if (typeof callback === 'string') {
      switch (callback) {
      case 'toggle':
        swapActiveLabel();
        break;
      case 'update':
        if (props.command) {
          await executeCommand();
        }
        break;
      }
    } else {
      if (callback?.exec) {
        await processExecCallback(callback);
      }
    }
  }
};

const processExecCallback = async (callback: ExecCallback) => {
  const command = callback.exec.cmd;
  let args = callback.exec.args ?? [];

  // format any args that might be template literals
  args = args.map((arg) => {
    try {
      return eval('`'+arg.replace(/`/g, '\\`')+'`');
    } catch (error) {
      return arg;
    }
  });

  await invoke('process_custom_command', {command, args, timeout: 1000});
};

const mouseoutUntoggle = () => {
  if (props.callbacks?.on_hover === 'toggle') {
    swapActiveLabel();
  }
};

</script>

<template>
  <span
    :data-toggle="!!activeLabelError"
    :title="activeLabelError ?? ''"
    :class="{error: !!activeLabelError}"
    @click.left="processCallback('on_left')"
    @click.middle="processCallback('on_middle')"
    @click.right="processCallback('on_right')"
    @mouseover="processCallback('on_hover')"
    @mouseout="mouseoutUntoggle()"
  >
    {{ activeLabelFormatted }}
  </span>
</template>
