<script setup lang="ts">

import moment from 'moment';
import {ref, onMounted} from 'vue';

type DateTimeProps = {
  format?: string,
  interval?: number
}

const props = defineProps<DateTimeProps>();
const currentDateTime = ref<Date | undefined>(undefined);

const updateCurrentDateTime = () => {
  currentDateTime.value = new Date();
};

onMounted(() => {
  const timer = setInterval(updateCurrentDateTime, props.interval ?? 1000);
  updateCurrentDateTime();
});

</script>

<template>
  <span>{{moment(currentDateTime).format(props.format ?? 'HH:mm:ss')}}</span>
</template>

<style scoped></style>
