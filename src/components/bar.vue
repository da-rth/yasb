<script setup lang="ts">

import {computed, onMounted, Ref, ref, onBeforeUnmount} from 'vue';
import {appWindow} from '@tauri-apps/api/window';
import {listen, Event as TauriEvent, UnlistenFn} from '@tauri-apps/api/event';
import {availableWidgets, Widgets} from './widgets';
import {invoke} from '@tauri-apps/api/tauri';
import log from '@/utils/log';
import UnknownWidget from './widgets/unknown.widget.vue';

enum BarEdge {
  Top = 'top',
  Left = 'left',
  Bottom = 'bottom',
  Right = 'right'
}

type ColumnBarWidgets = {
  left?: string[],
  middle?: string[],
  right?: string[]
}

interface IBarConfig {
  thickness?: number,
  edge?: BarEdge,
  screens?: string[],
  widgets?: ColumnBarWidgets,
  win_app_bar?: boolean,
  always_on_top?: boolean
}

const unlisteners: UnlistenFn[] = [];
const config: Ref<IBarConfig> = ref({});
const widgets: Ref<Widgets> = ref({
  left: [],
  middle: [],
  right: [],
});

let windowHiddenByuser = false;
let stylesheetElement: HTMLElement | undefined;

const barLabel = appWindow.label.slice(0, appWindow.label.lastIndexOf('_'));
const edgeClass = computed(() => {
  return config.value.edge ? `edge-${config.value.edge}` : '';
});

const onStylesChanged = (event: TauriEvent<string>) => {
  if (stylesheetElement && event.payload) {
    stylesheetElement.textContent = event.payload as string;
  }
};

const onHideAllWindows = (event: TauriEvent<boolean>) => {
  windowHiddenByuser = true;
  appWindow.hide();
};

const onShowAllWindows = (event: TauriEvent<boolean>) => {
  windowHiddenByuser = false;
  appWindow.show();
};

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
  const barStyles: string = await invoke('retrieve_styles');
  stylesheetElement = document.createElement('style');
  stylesheetElement.setAttribute('type', 'text/css');
  stylesheetElement.textContent = barStyles;
  document.head.appendChild(stylesheetElement);

  const barWidgets: any = await invoke('retrieve_widgets', {barLabel});
  widgets.value.left = Array.from(barWidgets.left.map((w: any) => Object.values(w)).flat());
  widgets.value.middle = Array.from(barWidgets.middle.map((w: any) => Object.values(w)).flat());
  widgets.value.right = Array.from(barWidgets.right.map((w: any) => Object.values(w)).flat());

  const barConfig: IBarConfig = await invoke('retrieve_config', {barLabel});
  config.value = barConfig;

  unlisteners.push(await listen('StylesChangedEvent', onStylesChanged));
  unlisteners.push(await listen('HideAllWindowsEvent', onHideAllWindows));
  unlisteners.push(await listen('ShowAllWindowsEvent', onShowAllWindows));
  unlisteners.push(await listen('FullscreenHideWindow', onFullscreenHide));
  unlisteners.push(await listen('FullscreenShowWindow', onFullscreenShow));

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
