<script setup lang="ts">
import { onMounted } from "vue"
import { appWindow, currentMonitor } from "@tauri-apps/api/window";
import { widgetMap } from "./components"

const widgets = {
  left: [
    {
      name: 'TextWidget',
      options: {
        text: 'Left',
        // href: 'http://example.com/'
      }
    }
  ],
  center: [
    {
      name: 'DateTimeWidget',
      options: {
        format: 'hh:mm:ss'
      }
    }
  ],
  right: [{
    name: 'TextWidget',
    options: {
      text: 'Right'
    }
  }]
}

onMounted(async () => {
  console.log("Monitor:", await appWindow.outerSize(), await appWindow.outerPosition());
});
</script>

<template>
  <div class="bar-container">
    <span class="bar-left widgets-container">
      <template v-for="widget in widgets.left" :key="widget">
        <component :is="widgetMap[widget.name]" v-bind="widget.options"></component>
      </template>
    </span>
    <span class="bar-center widget-container">
      <template v-for="widget in widgets.center" :key="widget">
        <component :is="widgetMap[widget.name]" v-bind="widget.options"></component>
      </template>
    </span>
    <span class="bar-right widget-container">
      <template v-for="widget in widgets.right" :key="widget">
        <component :is="widgetMap[widget.name]" v-bind="widget.options"></component>
      </template>
    </span>
  </div>
</template>

<style scoped>
.bar-container {
  display: flex;
  justify-content:  space-between;
  flex-wrap: wrap;
}

.widget-container {
  display: inline-block;
}
</style>
