<script setup lang="ts">
import { computed, onMounted, Ref, ref, onBeforeUnmount } from "vue";
import { appWindow, currentMonitor, LogicalPosition, PhysicalPosition, PhysicalSize } from "@tauri-apps/api/window";
import { listen, Event as TauriEvent, UnlistenFn } from '@tauri-apps/api/event'
import { availableWidgets, Widgets } from "./widgets";
import { invoke } from '@tauri-apps/api/tauri';
import { BarEdge, IBarConfig } from ".";
import log from "./log";
import UnknownWidget from "./widgets/unknown.widget.vue";

let windowHiddenByuser = false;
let eventUnlistenFunctions: UnlistenFn[] = [];
let stylesheetElement: HTMLElement | undefined;
let config: Ref<IBarConfig> = ref({});
let widgets: Ref<Widgets> = ref({
  left: [],
  middle: [],
  right: []
});

// const barIndex = parseInt(appWindow.label.slice(appWindow.label.lastIndexOf('_') + 1)) -1;
const barLabel = appWindow.label.slice(0, appWindow.label.lastIndexOf('_'));
const edgeClass = computed(() => config.value.edge ? `edge-${config.value.edge}` : '');

const onStylesChanged = (event: TauriEvent<string>) => {
  if (stylesheetElement && event.payload) {
    stylesheetElement.textContent = event.payload as string;
  }
}

const onHideAllWindows = (event: TauriEvent<boolean>) => {
  windowHiddenByuser = true;
  appWindow.hide();
}

const onShowAllWindows = (event: TauriEvent<boolean>) => {
  windowHiddenByuser = false;
  appWindow.show();
}

const onFullscreenHide = () => {
  // Don't hide or show windows explicitly hidden by the user
  if (config.value.always_on_top && !windowHiddenByuser) {
    appWindow.hide();
  }
};

const onFullscreenShow = () => {
  // Don't hide or show windows explicitly hidden by the user
  if (config.value.always_on_top && !windowHiddenByuser) {
    appWindow.show();
  }
};

onMounted(async () => {
  let bar_styles: string = await invoke('retrieve_styles');
  stylesheetElement = document.createElement('style');
  stylesheetElement.setAttribute("type", "text/css");
  stylesheetElement.textContent = bar_styles;
  document.head.appendChild(stylesheetElement);

  let bar_widgets: any = await invoke('retrieve_widgets', {barLabel});
  widgets.value.left = Array.from(bar_widgets.left.map((w: any) => Object.values(w)).flat());
  widgets.value.middle = Array.from(bar_widgets.middle.map((w: any) => Object.values(w)).flat());
  widgets.value.right = Array.from(bar_widgets.right.map((w: any) => Object.values(w)).flat());
  
  let bar_config: IBarConfig = await invoke('retrieve_config', {barLabel});
  config.value = bar_config;

  eventUnlistenFunctions.push(await listen("StylesChangedEvent", onStylesChanged));
  eventUnlistenFunctions.push(await listen("HideAllWindowsEvent", onHideAllWindows));
  eventUnlistenFunctions.push(await listen("ShowAllWindowsEvent", onShowAllWindows));
  eventUnlistenFunctions.push(await listen("FullscreenHideWindow", onFullscreenHide));
  eventUnlistenFunctions.push(await listen("FullscreenShowWindow", onFullscreenShow));

  await appWindow.show();
  await appWindow.setAlwaysOnTop(bar_config?.always_on_top ?? false);
  await log.info(`${appWindow.label} mounted.`)
});

onBeforeUnmount(async () => {
  stylesheetElement && document.head.removeChild(stylesheetElement);

  for (let unlistener of eventUnlistenFunctions) {
    unlistener();
  }
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
