<script setup lang="ts">
import moment from "moment";
import { ref, onMounted } from "vue";
import { DateTimeWidgetProps } from "~/bindings/widget/datetime/DateTimeWidgetProps";

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
