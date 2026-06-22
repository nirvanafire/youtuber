import { ipcMain, BrowserWindow } from "electron";
import { PythonManager } from "./python-manager";

let _proxyPort: number | null = null;

export function setProxyPort(port: number) {
  _proxyPort = port;
}

export function setupIpcHandlers(pythonManager: PythonManager, mainWindow: BrowserWindow) {
  ipcMain.handle("get-backend-port", () => {
    return _proxyPort ?? null;
  });

  ipcMain.handle("get-python-state", () => {
    const state = pythonManager.getState();
    return {
      port: _proxyPort ?? state.port,
      pythonPath: state.pythonPath,
      isEmbedded: state.isEmbedded,
      ready: state.ready,
    };
  });

  pythonManager.onReady((backendPort) => {
    // proxyPort is set by index.ts before this callback fires
    mainWindow.webContents.send("backend-ready", _proxyPort ?? backendPort);
  });

  pythonManager.onError((error) => {
    mainWindow.webContents.send("backend-error", error);
  });
}
