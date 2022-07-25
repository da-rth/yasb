<script setup lang="ts">
const props = defineProps({
  text: {
    type: String,
    required: false
  },
  href: {
      type: String,
      required: false
  }
});
</script>

<template>
  <span v-if="props.href"><a _target="_blank" :href="props.href">{{props.text}}</a></span>
  <span v-else>{{props.text}}</span>
</template>

<style scoped>
</style>
