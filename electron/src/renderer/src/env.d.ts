/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

interface ElectronAPI {
  getBackendPort: () => Promise<number | null>;
  getPythonState: () => Promise<{
    port: number | null;
    pythonPath: string;
    isEmbedded: boolean;
    ready: boolean;
  }>;
  onBackendReady: (callback: (port: number) => void) => void;
  onBackendError: (callback: (error: string) => void) => void;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
