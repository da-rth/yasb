<script setup lang="ts">
import moment from "moment"
import { ref, onMounted } from "vue"

type DateTimeProps = {
  format?: string,
  interval?: number
}

const props = defineProps<DateTimeProps>();
let currentDateTime = ref<Date | undefined>(undefined)

onMounted(() => {
    let timer = setInterval(updateCurrentDateTime, props.interval ?? 1000);
    updateCurrentDateTime()
})

function updateCurrentDateTime() {
    currentDateTime.value = new Date()
}
</script>

<template>
  <span>{{moment(currentDateTime).format(props.format ?? 'HH:mm:ss')}}</span>
</template>

<style scoped></style>
