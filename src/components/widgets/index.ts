import TextWidget from './text.widget.vue';
import DateTimeWidget from './datetime.widget.vue';
import CustomWidget from './custom.widget.vue';

export const availableWidgets = {
  TextWidget,
  DateTimeWidget,
  CustomWidget,
};

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
