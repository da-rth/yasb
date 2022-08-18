<script setup lang="ts">
import { computed, onMounted, Ref, ref, onBeforeUnmount } from "vue";
import { appWindow } from "@tauri-apps/api/window";
import { listen, Event as TauriEvent, UnlistenFn } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/tauri";
import { BarConfig } from "~/bindings/config/BarConfig";
import { ConfiguredWidgets } from "~/bindings/widget/ConfiguredWidgets";
import Widgets from "./widgets";
import log from "~/utils/log";

const unlisteners: UnlistenFn[] = [];
const config: Ref<BarConfig | undefined> = ref();
const widgets: Ref<ConfiguredWidgets> = ref({
  left: [],
  middle: [],
  right: [],
});

let windowHiddenByuser = false;
let stylesheetElement: HTMLElement | undefined;

const barLabel = appWindow.label.slice(0, appWindow.label.lastIndexOf("_"));
const edgeClass = computed(() => {
  return config.value?.edge ? `edge-${config.value?.edge}` : "";
});

const onStylesChanged = (event: TauriEvent<string>) => {
  if (stylesheetElement && event.payload) {
    stylesheetElement.textContent = event.payload as string;
  }
};

const onHideAllWindows = () => {
  windowHiddenByuser = true;
  appWindow.hide();
};

const onShowAllWindows = () => {
  windowHiddenByuser = false;
  appWindow.show();
};

const onHideFullscreen = () => {
  if (config.value?.always_on_top && !windowHiddenByuser) {
    appWindow.hide();
  }
};

const onShowFullscreen = () => {
  if (config.value?.always_on_top && !windowHiddenByuser) {
    appWindow.show();
  }
};

onMounted(async () => {
  stylesheetElement = document.createElement("style");
  stylesheetElement.setAttribute("type", "text/css");
  stylesheetElement.textContent = await invoke("retrieve_styles");
  document.head.appendChild(stylesheetElement);

  widgets.value = await invoke("retrieve_widgets", {
    barLabel,
  });
  console.log(widgets);
  config.value = await invoke("retrieve_config", { barLabel });

  unlisteners.push(await listen("StylesChangedEvent", onStylesChanged));
  unlisteners.push(await listen("HideAllWindowsEvent", onHideAllWindows));
  unlisteners.push(await listen("ShowAllWindowsEvent", onShowAllWindows));
  unlisteners.push(await listen("FullscreenHideWindow", onHideFullscreen));
  unlisteners.push(await listen("FullscreenShowWindow", onShowFullscreen));

  await appWindow.show();
  await appWindow.setAlwaysOnTop(config.value?.always_on_top ?? false);
  await log.info(`${appWindow.label} mounted.`);
});

onBeforeUnmount(async () => {
  stylesheetElement && document.head.removeChild(stylesheetElement);

  for (const unlistener of unlisteners) {
    unlistener();
  }
});
</script>

<template>
  <div :class="['bar', edgeClass, barLabel]">
    <div class="widgets-container bar-left">
      <template v-for="(w, i) in widgets.left" :key="`l_${w.kind}_${i}`">
        <component
          v-bind="w"
          :id="w.kind"
          :is="w.kind in Widgets ? Widgets[w.kind] : Widgets.UnknownWidget"
        ></component>
      </template>
    </div>

    <div class="widgets-container bar-middle">
      <template v-for="(w, i) in widgets.middle" :key="`m_${w.kind}_${i}`">
        <component
          v-bind="w"
          :id="w.kind"
          :is="w.kind in Widgets ? Widgets[w.kind] : Widgets.UnknownWidget"
        ></component>
      </template>
    </div>

    <div class="widgets-container bar-right">
      <template v-for="(w, i) in widgets.right" :key="`r_${w.kind}_${i}`">
        <component
          v-bind="w"
          :id="w.kind"
          :is="w.kind in Widgets ? Widgets[w.kind] : Widgets.UnknownWidget"
        ></component>
      </template>
    </div>
  </div>
</template>
