<script setup lang="ts">
import type { UnknownWidgetProps } from "~/bindings/widget/unknown/UnknownWidgetProps";

const props = defineProps<UnknownWidgetProps>();
</script>

<template>
  <span
    :class="['widget', 'error']"
    :title="`${$props.kind} is not a valid widget.`"
    >{{ props.kind }}</span
  >
</template>
