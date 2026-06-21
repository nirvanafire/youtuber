import { app, BrowserWindow } from "electron";
import path from "path";
import { PythonManager } from "./python-manager";
import { ApiProxy } from "./api-proxy";
import { setupIpcHandlers, setProxyPort } from "./ipc-handlers";
import log from "./logger";

process.on("uncaughtException", (err) => {
  log.error("未捕获异常:", err);
});

process.on("unhandledRejection", (reason) => {
  log.error("未处理的 Promise 拒绝:", reason);
});

let mainWindow: BrowserWindow | null = null;
const pythonManager = new PythonManager();
const apiProxy = new ApiProxy();
const PROXY_PORT = 15000 + Math.floor(Math.random() * 5000);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    show: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      devTools: true,
    },
  });

  pythonManager.onReady(async (backendPort) => {
    await apiProxy.start(PROXY_PORT, backendPort);
    mainWindow?.show();
  });

  pythonManager.onError((error) => {
    log.error("Python manager error:", error);
    mainWindow?.show();
  });

  setProxyPort(PROXY_PORT);
  setupIpcHandlers(pythonManager, mainWindow);

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/dist/index.html"));
  }

  // F12 to toggle DevTools
  mainWindow.webContents.on("before-input-event", (_event, input) => {
    if (input.key === "F12") {
      mainWindow?.webContents.toggleDevTools();
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  createWindow();
  await pythonManager.start();
});

app.on("before-quit", async () => {
  apiProxy.stop();
  await pythonManager.stop();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
