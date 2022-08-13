<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import { invoke } from "@tauri-apps/api/tauri";
import { ref, onMounted } from "vue";
import { CatCommandResponse } from "~/bindings/widget/cat/CatCommandResponse";
import type { CatWidgetProps } from "~/bindings/widget/cat/CatWidgetProps";

const props = defineProps<CatWidgetProps>();

// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
let data: any;
let activeLabel: string;
let commandResult: CatCommandResponse;

const defaultLabel = "CatWidget";
const activeLabelError = ref<string | null>(null);
const activeLabelFormatted = ref<string>(props.label ?? defaultLabel);

onMounted(async () => {
  activeLabel = props.label ?? defaultLabel;

  console.log(props.target);

  if (props.target?.file) {
    await executeCommand();

    if (props.target.interval ?? 0 > 0) {
      setInterval(executeCommand, props.target.interval!);
    }
  }
});

const executeCommand = async () => {
  commandResult = await invoke("process_cat_command", {
    target: props.target?.file,
  });

  updateActiveLabel();
};

const updateActiveLabel = () => {
  if (commandResult.stdout) {
    try {
      data = JSON.parse(commandResult.stdout);
    } catch {
      data = commandResult.stdout.replace("\n", "\\n");
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
    const file = props.target?.file;
    const status = commandResult.status ?? 1;

    if (commandResult.stderr) {
      activeLabelError.value = `Cat: "${file}" exited with error: ${status}\n\n${commandResult.stderr}`;
    } else {
      activeLabelError.value = `Unknown Error. Check log for details.`;
    }

    activeLabelFormatted.value = file ?? "error";
  }
};
</script>

<template>
  <span
    :data-toggle="!!activeLabelError"
    :title="activeLabelError ?? ''"
    :class="['widget', props.class, { error: !!activeLabelError }]"
  >
    {{ activeLabelFormatted }}
  </span>
</template>
