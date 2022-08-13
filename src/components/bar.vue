<script setup lang="ts">
import { computed, onMounted, Ref, ref, onBeforeUnmount } from "vue";
import { appWindow } from "@tauri-apps/api/window";
import { listen, Event as TauriEvent, UnlistenFn } from "@tauri-apps/api/event";
import { availableWidgets } from "./widgets";
import { invoke } from "@tauri-apps/api/tauri";
import { BarConfig } from "~/bindings/config/BarConfig";
import { ConfiguredWidget } from "~/bindings/widget/ConfiguredWidget";
import { ConfiguredWidgets } from "~/bindings/widget/ConfiguredWidgets";
import { ConfiguredOrDefaultWidgets } from "~/bindings/widget/base/ConfiguredOrDefaultWidgets";
import UnknownWidget from "./widgets/unknown.widget.vue";
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
  const barStyles: string = await invoke("retrieve_styles");
  stylesheetElement = document.createElement("style");
  stylesheetElement.setAttribute("type", "text/css");
  stylesheetElement.textContent = barStyles;
  document.head.appendChild(stylesheetElement);

  const barWidgets: ConfiguredOrDefaultWidgets = await invoke(
    "retrieve_widgets",
    { barLabel }
  );

  widgets.value.left = Array.from(
    barWidgets.left.map((w) => Object.values(w) as ConfiguredWidget[]).flat()
  );
  widgets.value.middle = Array.from(
    barWidgets.middle.map((w) => Object.values(w) as ConfiguredWidget[]).flat()
  );
  widgets.value.right = Array.from(
    barWidgets.right.map((w) => Object.values(w) as ConfiguredWidget[]).flat()
  );

  const barConfig: BarConfig = await invoke("retrieve_config", { barLabel });
  config.value = barConfig;

  unlisteners.push(await listen("StylesChangedEvent", onStylesChanged));
  unlisteners.push(await listen("HideAllWindowsEvent", onHideAllWindows));
  unlisteners.push(await listen("ShowAllWindowsEvent", onShowAllWindows));
  unlisteners.push(await listen("FullscreenHideWindow", onHideFullscreen));
  unlisteners.push(await listen("FullscreenShowWindow", onShowFullscreen));

  await appWindow.show();
  await appWindow.setAlwaysOnTop(barConfig?.always_on_top ?? false);
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
  <div id="bar" :class="[barLabel, edgeClass]">
    <div class="widgets-container bar-left">
      <template v-for="(widget, _idx) in widgets.left">
        <component
          v-if="widget.kind in availableWidgets"
          v-bind="widget"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :key="`left_${widget.kind}_${_idx}`"
        ></component>
        <UnknownWidget
          :kind="widget.kind"
          :key="`left_unknown_${widget.kind}_${_idx}`"
          v-else
        />
      </template>
    </div>

    <div class="widgets-container bar-middle">
      <template v-for="(widget, _idx) in widgets.middle">
        <component
          v-if="widget.kind in availableWidgets"
          v-bind="widget"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :key="`middle_${widget.kind}_${_idx}`"
        ></component>
        <UnknownWidget
          :kind="widget.kind"
          :key="`middle_unknown_${widget.kind}_${_idx}`"
          v-else
        />
      </template>
    </div>

    <div class="widgets-container bar-right">
      <template v-for="(widget, _idx) in widgets.right">
        <component
          v-if="widget.kind in availableWidgets"
          v-bind="widget"
          :is="availableWidgets[widget.kind]"
          :id="widget.kind"
          :key="`right_${widget.kind}_${_idx}`"
        ></component>
        <UnknownWidget
          :kind="widget.kind"
          :key="`right_unknown_${widget.kind}_${_idx}`"
          v-else
        />
      </template>
    </div>
  </div>
</template>
