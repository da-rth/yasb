import TextWidget from "./Text.vue";
import DateTimeWidget from "./DateTime.vue";

export const availableWidgets = {
  TextWidget,
  DateTimeWidget
}

export interface Widget {
  kind: WidgetKind,
  class?: String
};

export type Widgets = {
  left: Widget[],
  middle: Widget[],
  right: Widget[]
}

export type WidgetKind = keyof typeof availableWidgets;
