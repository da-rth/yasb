<!-- eslint-disable @typescript-eslint/no-non-null-assertion -->
<script setup lang="ts">
import { CallbackEvent } from "~/bindings/widget/base/CallbackEvent";
import { CallbackType } from "~/bindings/widget/base/CallbackType";
import { WidgetCallbacks } from "~/bindings/widget/base/WidgetCallbacks";
import { CallbackTypeExecOptions } from "~/bindings/widget/base/CallbackTypeExecOptions";

const props = defineProps<{
  callbacks?: WidgetCallbacks | null;
  onToggle?: () => Promise<void>;
  onUpdate?: () => Promise<void>;
  onExec?: (exec_options: CallbackTypeExecOptions) => Promise<void>;
}>();

const handleCallback = async (callbackEvent: CallbackEvent) => {
  if (props.callbacks) {
    const callbackType: CallbackType | null = props.callbacks[callbackEvent];

    if (callbackEvent === "on_hover" && callbackType === "tooltip") return;

    if (typeof callbackType === "string") {
      switch (callbackType) {
        case "toggle":
          await props.onToggle?.();
          break;
        case "update":
          await props.onUpdate?.();
          break;
      }
    } else {
      if (callbackType?.exec) {
        await props.onExec?.(callbackType?.exec);
      }
    }
  }
};

const handleMouseOut = () => {
  if (props.callbacks?.on_hover === "toggle") {
    props.onToggle?.();
  }
};
</script>

<template>
  <span
    @click.left="handleCallback('on_left')"
    @click.middle="handleCallback('on_middle')"
    @click.right="handleCallback('on_right')"
    @mouseover="handleCallback('on_hover')"
    @mouseout="handleMouseOut()"
  >
    <slot></slot>
  </span>
</template>
