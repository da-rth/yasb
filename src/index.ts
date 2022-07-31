export enum BarEdge {
  Top = "top",
  Left = "left",
  Bottom = "bottom",
  Right = "right"
}

type ColumnBarWidgets = {
  left?: string[],
  middle?: string[],
  right?: string[]
}

export interface IBarConfig {
  thickness?: number,
  edge?: BarEdge,
  screens?: string[],
  widgets?: ColumnBarWidgets,
  win_app_bar?: boolean,
  always_on_top?: boolean
}