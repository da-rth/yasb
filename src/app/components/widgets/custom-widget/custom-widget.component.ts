import { Component, Inject, ViewEncapsulation } from "@angular/core";
import { WIDGET_PROPS } from "..";
import { CustomWidgetProps } from "../../../../bindings/widget/custom/CustomWidgetProps";

@Component({
    selector: "custom-widget",
    templateUrl: "./custom-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class CustomWidgetComponent {
    public activeLabelFormatted = "todo";
    public constructor(@Inject(WIDGET_PROPS) public props?: CustomWidgetProps) {}
}

/**

<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import type { CallbackTypeExecOptions } from "~/bindings/widget/base/CallbackTypeExecOptions";
import type { CustomCommandResponse } from "~/bindings/widget/custom/CustomCommandResponse";
import type { CustomWidgetProps } from "~/bindings/widget/custom/CustomWidgetProps";
import { invoke } from "@tauri-apps/api/tauri";
import { ref, onMounted } from "vue";
import { tryFormatArgsEval, tryFormatEval } from "../../utils/format";
import WidgetWrapper from "../WidgetWrapper.vue";
import Log from "~/utils/log";

const props = defineProps<CustomWidgetProps>();
const defaultLabel = "CustomWidget";
const activeLabelTooltip = ref<string | null>(null);
const activeLabelError = ref<string | null>(null);
const activeLabelFormatted = ref<string>(
  props.label_alt ?? props.label ?? defaultLabel
);

// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
let commandResultData: any;
let showAltLabel = false;
const unformattedActiveTooltip = props.label_tooltip ?? "";
let unformattedActiveLabel = props.label ?? defaultLabel;
let commandResult: CustomCommandResponse;

onMounted(async () => {
  if (props.command) {
    await executeCustomCommand();

    if (props.command.interval ?? 0 > 0) {
      setInterval(executeCustomCommand, props.command.interval ?? 1000);
    }
  }
});

const executeCustomCommand = async () => {
  commandResult = await invoke("process_custom_command", {
    command: props.command?.cmd,
    args: props.command?.args ?? [],
    timeout: Math.floor((props.command?.interval ?? 1000) / 2),
  });

  updateActiveLabel();
};

const updateActiveLabel = () => {
  if (commandResult.stdout) {
    try {
      commandResultData = JSON.parse(commandResult.stdout);
    } catch {
      commandResultData = commandResult.stdout.replace("\n", "\\n");
    }
    try {
      activeLabelTooltip.value = props.label_tooltip
        ? tryFormatEval(unformattedActiveTooltip, commandResultData)
        : null;
      activeLabelFormatted.value = tryFormatEval(
        unformattedActiveLabel,
        commandResultData
      );
      activeLabelError.value = null;
    } catch (error) {
      activeLabelTooltip.value = unformattedActiveTooltip;
      activeLabelFormatted.value = unformattedActiveLabel;
      activeLabelError.value = `Error formatting label:\n\n${
        (error as Error).message
      }`;
    }
  } else {
    // If no stdout, format error tooltip
    const cmd = props.command?.cmd;
    const args = ` ${(props.command?.args ?? []).join(" ")}`;
    const status = commandResult.status ?? 1;

    activeLabelError.value = `exited with code: ${status}\n\n${cmd}${args}\n\nstderr: ${
      commandResult.stderr ?? "empty"
    }`;
    activeLabelFormatted.value = cmd ?? unformattedActiveLabel;
  }
};

const toggleActiveLabel = async () => {
  showAltLabel = !showAltLabel;
  unformattedActiveLabel =
    (showAltLabel ? props.label_alt : props.label) ?? defaultLabel;
  updateActiveLabel();
};

const onCallbackExec = async (exec_options: CallbackTypeExecOptions) => {
  const command = exec_options.cmd;
  const args = tryFormatArgsEval(exec_options?.args ?? [], commandResultData);
  await invoke("process_custom_command", { command, args, timeout: 1000 });
  Log.info(`UnknownWidget: ${command} ${args}`);
};

 */
