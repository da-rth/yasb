<script setup lang="ts">
import { TextWidgetProps } from "~/bindings/widget/text/TextWidgetProps";

const props = defineProps<TextWidgetProps>();
</script>

<template>
  <span :class="['widget', props.class]">{{ props.text ?? "Text" }}</span>
</template>
