<script setup lang="ts">
import { computed, onMounted, Ref, ref } from "vue";
import { appWindow } from "@tauri-apps/api/window";
import { availableWidgets, WidgetKind, Widgets, Widget } from "./widgets";
import { invoke } from '@tauri-apps/api/tauri';
import UnknownWidget from "./widgets/UnknownWidget.vue";
import { IBarConfig } from ".";
let config: Ref<IBarConfig> = ref({});
let widgets: Ref<Widgets> = ref({
  left: [],
  middle: [],
  right: []
});

// const barIndex = parseInt(appWindow.label.slice(appWindow.label.lastIndexOf('_') + 1)) -1;
const barLabel = appWindow.label.slice(0, appWindow.label.lastIndexOf('_'));
const edgeClass = computed(() => config.value.edge ? `edge-${config.value.edge}` : '');

onMounted(async () => {
  let bar_config: IBarConfig = await invoke('retrieve_config', {barLabel});
  config.value = bar_config;
  let bar_widgets: any = await invoke('retrieve_widgets', {barLabel});
  widgets.value.left = Array.from(bar_widgets.left.map((w: any) => Object.values(w)).flat());
  widgets.value.middle = Array.from(bar_widgets.middle.map((w: any) => Object.values(w)).flat());
  widgets.value.right = Array.from(bar_widgets.right.map((w: any) => Object.values(w)).flat());
  let bar_styles: string = await invoke('retrieve_styles');
  document.head.insertAdjacentHTML("beforeend", `<style>${bar_styles}</style>`);
  console.log("styles", bar_styles);
  console.log(bar_widgets);
  console.log(bar_config);
});
</script>

<template>
  <div id="bar" :class="[barLabel, edgeClass]">
    <div class="widgets-container bar-left">
      <template v-for="(widget, _idx) in widgets.left" :key="`l_${widget.kind}_${_idx}`">
       <component
          v-if="widget.kind in availableWidgets"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :class="widget.class"
          class="widget"
          v-bind="widget"
        ></component>
        <UnknownWidget :kind="widget.kind" v-else/>
      </template>
    </div>
    
    <div class="widgets-container bar-middle">
      <template v-for="(widget, _idx) in widgets.middle" :key="`m_${widget.kind}_${_idx}`">
        <component
          v-if="widget.kind in availableWidgets"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :class="widget.class"
          class="widget"
          v-bind="widget"
        ></component>
        <UnknownWidget :kind="widget.kind" v-else/>
      </template>
    </div>
    
    <div class="widgets-container bar-right">
      <template v-for="(widget, _idx) in widgets.right" :key="`r_${widget.kind}_${_idx}`">
        <component
          v-if="widget.kind in availableWidgets"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :class="widget.class"
          class="widget"
          v-bind="widget"
        ></component>
        <UnknownWidget :kind="widget.kind" v-else/>
      </template>
    </div>
  </div>
</template>
