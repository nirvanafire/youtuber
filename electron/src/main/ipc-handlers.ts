import { ipcMain, BrowserWindow } from "electron";
import { PythonManager } from "./python-manager";

export function setupIpcHandlers(pythonManager: PythonManager, mainWindow: BrowserWindow) {
  ipcMain.handle("get-backend-port", () => {
    const state = pythonManager.getState();
    return state.port;
  });

  ipcMain.handle("get-python-state", () => {
    const state = pythonManager.getState();
    return {
      port: state.port,
      pythonPath: state.pythonPath,
      isEmbedded: state.isEmbedded,
      ready: state.ready,
    };
  });

  pythonManager.onReady((port) => {
    mainWindow.webContents.send("backend-ready", port);
  });

  pythonManager.onError((error) => {
    mainWindow.webContents.send("backend-error", error);
  });
}
