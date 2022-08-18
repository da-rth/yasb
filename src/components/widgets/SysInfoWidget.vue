<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import { invoke } from "@tauri-apps/api/tauri";
import { ref, onMounted } from "vue";
import { tryFormatArgsEval, tryFormatEval } from "../../utils/format";
import { SysInfoWidgetProps } from "../../bindings/widget/sysinfo/SysInfoWidgetProps";
import { SystemInformation } from "../../bindings/widget/sysinfo/SystemInformation";
import WidgetWrapper from "../WidgetWrapper.vue";
import { CallbackTypeExecOptions } from "../../bindings/widget/base/CallbackTypeExecOptions";

const DEFAULT_LABEL = "host: ${data.sys.host}";
const DEFAULT_TOOLTIP = "${JSON.stringify(data, null, 2)}";
const props = defineProps<SysInfoWidgetProps>();
const activeLabelTooltip = ref<string | null>(null);
const activeLabelFormatted = ref<string>(
  props.label_alt ?? props.label ?? DEFAULT_LABEL
);
const isHidden = ref<boolean>(true);
const isError = ref<boolean>(false);

let activeLabel: string = props.label ?? DEFAULT_LABEL;
let showAltLabel = false;
let sysInfo: SystemInformation | unknown;

onMounted(async () => {
  await invoke("get_sys_info").then((info) => {
    isHidden.value = false;
    sysInfo = info;
    updateLabels();
    props.interval && setInterval(queryInfo, props.interval);
  });
});

const queryInfo = async () => {
  await invoke("get_sys_info").then((info) => {
    sysInfo = info;
    updateLabels();
  });
};

const updateLabels = () => {
  try {
    const tooltip = props.label_tooltip ?? DEFAULT_TOOLTIP;
    activeLabelTooltip.value = tooltip ? tryFormatEval(tooltip, sysInfo) : null;
  } catch (error) {
    activeLabelTooltip.value = `Error formatting tooltip:\n\n${
      (error as Error).message
    }`;
  }

  try {
    activeLabelFormatted.value = tryFormatEval(activeLabel, sysInfo);
    isError.value = false;
  } catch (error) {
    activeLabelFormatted.value = activeLabel;
    activeLabelTooltip.value = `Error formatting active label:\n\n${
      (error as Error).message
    }`;
    isError.value = true;
  }
};

const onCallbackToggle = async () => {
  showAltLabel = !showAltLabel;
  activeLabel = (showAltLabel ? props.label_alt : props.label) ?? DEFAULT_LABEL;
  updateLabels();
};

const onCallbackExec = async (exec_options: CallbackTypeExecOptions) => {
  const command = exec_options.cmd;
  const args = tryFormatArgsEval(exec_options?.args ?? [], sysInfo);
  await invoke("process_custom_command", { command, args, timeout: 1000 });
};
</script>

<template>
  <WidgetWrapper
    v-bind="{ callbacks: props.callbacks }"
    :on-toggle="onCallbackToggle"
    :on-exec="onCallbackExec"
    :class="['widget', props.class, { error: isError, hidden: isHidden }]"
    :data-toggle="!!activeLabelTooltip"
    :title="activeLabelTooltip ?? ''"
  >
    {{ activeLabelFormatted }}
  </WidgetWrapper>
</template>
