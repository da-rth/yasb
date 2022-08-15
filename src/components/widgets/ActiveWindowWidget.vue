<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import type { ActiveWindowPayload } from "~/bindings/widget/active_window/ActiveWindowPayload";
import type { ActiveWindowWidgetProps } from "~/bindings/widget/active_window/ActiveWindowWidgetProps";
import type { CallbackTypeExecOptions } from "~/bindings/widget/base/CallbackTypeExecOptions";
import { listen, UnlistenFn, Event as TauriEvent } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/tauri";
import { currentMonitor } from "@tauri-apps/api/window";
import { ref, onMounted, onBeforeUnmount } from "vue";
import { tryFormatArgsEval, tryFormatEval } from "../../utils/format";
import WidgetWrapper from "../WidgetWrapper.vue";
import Log from "~/utils/log";

const APP_TITLE = "yasb";
const APP_PROC_NAME = "yasb.exe";
const DEFAULT_LABEL = "${win.title} ${win.class} ${win.process}";

const props = defineProps<ActiveWindowWidgetProps>();
const activeLabelTooltip = ref<string | null>(null);
const activeLabelFormatted = ref<string>("");
const isHidden = ref<boolean>(true);
const isError = ref<boolean>(false);
const ignoredProcesses: string[] = [
  "SearchHost.exe",
  "ShellExperienceHost.exe",
  ...(props.ignore?.process ?? []),
];
const ignoredTitles: string[] = [...(props.ignore?.class ?? [])];
const ignoredClasses: string[] = [
  "WorkerW",
  "NotifyIconOverflowWindow",
  "XamlExplorerHostIslandWindow",
  "Windows.UI.Core.CoreWindow",
  ...(props.ignore?.title ?? []),
];

const explorerNavigationClasses: string[] = [
  "SHELLDLL_DefView",
  "Windows.UI.Input.InputSite.WindowClass",
  "ToolbarWindow32",
  "SysTreeView32",
  "DirectUIHWND",
  "ComboLBox",
];

let activeWindowUnlistener: UnlistenFn;
let activeLabel: string = props.label ?? DEFAULT_LABEL;
let currentMonitorName: string | null | undefined;
let showAltLabel = false;
let win: ActiveWindowPayload;

onMounted(async () => {
  currentMonitorName = (await currentMonitor())?.name;

  activeWindowUnlistener = await listen(
    "ActiveWindowChanged",
    onActiveWindowChange
  );

  await invoke("init_win_event_hook");
  await invoke("detect_foreground_window");
});

onBeforeUnmount(async () => {
  activeWindowUnlistener && activeWindowUnlistener();
});

const onActiveWindowChange = async (event: TauriEvent<ActiveWindowPayload>) => {
  Log.info(event.payload.title + " " + event.payload.class);
  if (
    (!event.payload.title && event.payload.class != "WorkerW") ||
    event.payload.title == APP_TITLE ||
    event.payload.exe_name == APP_PROC_NAME
  ) {
    return;
  }

  // If navigation has changed on explorer, get the new foreground title
  if (explorerNavigationClasses.includes(event.payload.class ?? "")) {
    await invoke("detect_foreground_window");
    return;
  }

  win = event.payload;

  if (
    ignoredProcesses.includes(win.exe_name ?? "") ||
    ignoredClasses.includes(win.class ?? "") ||
    ignoredTitles.includes(win.title ?? "")
  ) {
    isHidden.value = true;
  } else {
    isHidden.value = !!props.exclusive && win.monitor != currentMonitorName;
    updateLabels();
  }
};

const updateLabels = () => {
  try {
    activeLabelTooltip.value = props.label_tooltip
      ? tryFormatEval(props.label_tooltip, win)
      : null;
  } catch (error) {
    activeLabelTooltip.value = `Error formatting tooltip:\n\n${
      (error as Error).message
    }`;
  }

  try {
    activeLabelFormatted.value = tryFormatEval(activeLabel, win);
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
  const args = tryFormatArgsEval(exec_options?.args ?? [], win);
  await invoke("process_custom_command", { command, args, timeout: 1000 });
  Log.info(`ActiveWindowWidget: ${command} ${args}`);
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
