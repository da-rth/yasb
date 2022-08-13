<script setup lang="ts">
const props = defineProps({
  kind: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <span class="widget" id="UnknownWidget" placeholder="unknown widget">{{
    props.kind
  }}</span>
</template>

<style scoped>
#UnknownWidget {
  background: red;
  padding: 2px 5px;
  color: black;
  font-weight: bold;
}
</style>
