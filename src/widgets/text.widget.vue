<script setup lang="ts">

type TextWidgetProps = {
  text?: string
}

const props = defineProps<TextWidgetProps>();
</script>

<template>
  <span>{{props.text ?? 'Text'}}</span>
</template>
