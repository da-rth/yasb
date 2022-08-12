// eslint-disable-next-line spaced-comment
/// <reference types="vite/client" />

declare module '*.vue' {
  import type {DefineComponent} from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
