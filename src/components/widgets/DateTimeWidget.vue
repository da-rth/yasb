<script setup lang="ts">
import type { DateTimeWidgetProps } from "~/bindings/widget/datetime/DateTimeWidgetProps";
import { ref, onMounted } from "vue";
import moment from "moment";

const props = defineProps<DateTimeWidgetProps>();
const currentDateTime = ref<Date | undefined>(undefined);

const updateCurrentDateTime = () => {
  currentDateTime.value = new Date();
};

onMounted(() => {
  setInterval(updateCurrentDateTime, props.interval ?? 1000);
  updateCurrentDateTime();
});
</script>

<template>
  <span :class="['widget', props.class]">{{
    moment(currentDateTime).format(props.format ?? "HH:mm:ss")
  }}</span>
</template>

<style scoped></style>
