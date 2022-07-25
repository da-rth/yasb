<script setup lang="ts">
import moment from "moment"
import { ref, onMounted } from "vue"

const props = defineProps({
  format: {
      type: String,
      required: false,
      default: 'hh:mm:ss'
  },
  interval: {
      type: Number,
      required: false,
      default: 1000
  }
});

let currentDateTime = ref<Date | undefined>(undefined)

onMounted(() => {
    let timer = setInterval(updateCurrentDateTime, props.interval);
    updateCurrentDateTime()
})

function updateCurrentDateTime() {
    currentDateTime.value = new Date()
}
</script>

<template>
  <span>{{moment(currentDateTime).format(props.format)}}</span>
</template>

<style scoped></style>
