<script setup lang="ts">
const props = defineProps({
  text: {
    type: String,
    required: false,
    default: 'Text'
  },
  href: {
      type: String,
      required: false
  }
});
</script>

<template>
  <span class="text" v-if="props.href"><a _target="_blank" :href="props.href">{{props.text}}</a></span>
  <span class="text" v-else>{{props.text}}</span>
</template>

<style scoped>
</style>
