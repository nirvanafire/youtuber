import { app, BrowserWindow } from "electron";
import path from "path";
import { PythonManager } from "./python-manager";
import { ApiProxy } from "./api-proxy";
import { setupIpcHandlers } from "./ipc-handlers";

let mainWindow: BrowserWindow | null = null;
const pythonManager = new PythonManager();
const apiProxy = new ApiProxy();
const PROXY_PORT = 15000 + Math.floor(Math.random() * 5000);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  setupIpcHandlers(pythonManager, mainWindow);

  pythonManager.onReady((backendPort) => {
    apiProxy.start(PROXY_PORT, backendPort);
    mainWindow?.webContents.send("backend-ready", PROXY_PORT);
    mainWindow?.show();
  });

  pythonManager.onError((error) => {
    console.error("Python manager error:", error);
    mainWindow?.webContents.send("backend-error", error);
    mainWindow?.show();
  });

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/dist/index.html"));
  }

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
