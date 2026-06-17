import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  getBackendPort: () => ipcRenderer.invoke("get-backend-port"),
  getPythonState: () => ipcRenderer.invoke("get-python-state"),
  onBackendReady: (callback: (port: number) => void) => {
    ipcRenderer.on("backend-ready", (_event, port) => callback(port));
  },
  onBackendError: (callback: (error: string) => void) => {
    ipcRenderer.on("backend-error", (_event, error) => callback(error));
  },
});
