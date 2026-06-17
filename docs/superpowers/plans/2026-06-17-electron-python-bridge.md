# Electron-Python Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the bridge layer between Electron main process and Python FastAPI backend — process lifecycle management, port communication, API proxy, and frontend loading state.

**Architecture:** Electron main process spawns Python backend as child process, reads PORT from stdout, health-checks until ready, proxies API/WebSocket from renderer, and handles crash recovery.

**Tech Stack:** Node.js, Electron, child_process, http-proxy, WebSocket

---

## File Structure

```
electron/src/main/
├── index.ts                # Modified: integrate python-manager
├── python-manager.ts       # Python process lifecycle
├── api-proxy.ts            # HTTP + WebSocket proxy
├── ipc-handlers.ts         # IPC handlers for renderer
└── preload.ts              # Modified: expose backend API
```

---

## Task 1: Python Manager — Environment Detection

**Files:**
- Create: `electron/src/main/python-manager.ts`
- Modify: `electron/src/main/index.ts`

- [ ] **Step 1: Create python-manager.ts with detection logic**

```typescript
// electron/src/main/python-manager.ts
import { spawn, execFile, ChildProcess } from "child_process";
import path from "path";
import net from "net";

const PYTHON_COMMANDS = ["python3", "python", "py"];
const MIN_PYTHON_VERSION = [3, 10];
const MAX_RESTARTS = 3;
const HEALTH_CHECK_INTERVAL = 500;
const HEALTH_CHECK_TIMEOUT = 30000;

export interface PythonManagerState {
  port: number | null;
  pythonPath: string;
  isEmbedded: boolean;
  process: ChildProcess | null;
  ready: boolean;
}

export class PythonManager {
  private state: PythonManagerState = {
    port: null,
    pythonPath: "",
    isEmbedded: false,
    process: null,
    ready: false,
  };
  private restartCount = 0;
  private onReadyCallback: ((port: number) => void) | null = null;
  private onErrorCallback: ((error: string) => void) | null = null;

  onReady(callback: (port: number) => void) {
    this.onReadyCallback = callback;
  }

  onError(callback: (error: string) => void) {
    this.onErrorCallback = callback;
  }

  getState(): PythonManagerState {
    return { ...this.state };
  }

  async detectPython(): Promise<string | null> {
    for (const cmd of PYTHON_COMMANDS) {
      try {
        const version = await this.getPythonVersion(cmd);
        if (version && this.isVersionValid(version)) {
          return cmd;
        }
      } catch {}
    }
    return null;
  }

  private getPythonVersion(cmd: string): Promise<string | null> {
    return new Promise((resolve) => {
      execFile(cmd, ["--version"], { timeout: 5000 }, (err, stdout) => {
        if (err) {
          resolve(null);
          return;
        }
        const match = stdout.match(/Python (\d+\.\d+\.\d+)/);
        resolve(match ? match[1] : null);
      });
    });
  }

  private isVersionValid(version: string): boolean {
    const parts = version.split(".").map(Number);
    return (
      parts[0] > MIN_PYTHON_VERSION[0] ||
      (parts[0] === MIN_PYTHON_VERSION[0] && parts[1] >= MIN_PYTHON_VERSION[1])
    );
  }

  async start(): Promise<void> {
    const pythonCmd = await this.detectPython();
    if (!pythonCmd) {
      // Try embedded Python
      const embeddedPath = this.getEmbeddedPythonPath();
      if (embeddedPath) {
        this.state.pythonPath = embeddedPath;
        this.state.isEmbedded = true;
      } else {
        this.onErrorCallback?.("未找到 Python 3.10+ 环境");
        return;
      }
    } else {
      this.state.pythonPath = pythonCmd;
      this.state.isEmbedded = false;
    }

    await this.spawnBackend();
  }

  private getEmbeddedPythonPath(): string | null {
    const isProd = !process.env.NODE_ENV || process.env.NODE_ENV === "production";
    if (!isProd) return null;

    const resourcesPath = process.resourcesPath;
    const platform = process.platform;
    if (platform === "win32") {
      return path.join(resourcesPath, "backend", "python", "python.exe");
    }
    return path.join(resourcesPath, "backend", "python", "bin", "python3");
  }

  private async spawnBackend(): Promise<void> {
    const backendScript = this.getBackendScriptPath();

    return new Promise((resolve, reject) => {
      const proc = spawn(this.state.pythonPath, [backendScript], {
        stdio: ["pipe", "pipe", "pipe"],
        env: { ...process.env },
      });

      this.state.process = proc;
      let portFound = false;
      let outputBuffer = "";

      proc.stdout?.on("data", (data: Buffer) => {
        outputBuffer += data.toString();
        const lines = outputBuffer.split("\n");
        outputBuffer = lines.pop() || "";

        for (const line of lines) {
          const portMatch = line.match(/PORT=(\d+)/);
          if (portMatch) {
            this.state.port = parseInt(portMatch[1], 10);
            portFound = true;
            this.waitForHealthCheck().then(() => {
              this.state.ready = true;
              this.restartCount = 0;
              this.onReadyCallback?.(this.state.port!);
              resolve();
            });
          }
        }
      });

      proc.stderr?.on("data", (data: Buffer) => {
        console.error(`[Python stderr] ${data.toString()}`);
      });

      proc.on("error", (err) => {
        this.onErrorCallback?.(`Python 进程启动失败: ${err.message}`);
        reject(err);
      });

      proc.on("exit", (code) => {
        this.state.ready = false;
        this.state.process = null;
        if (!portFound) {
          this.onErrorCallback?.(`Python 进程退出，代码: ${code}`);
          reject(new Error(`Python exited with code ${code}`));
        } else if (this.restartCount < MAX_RESTARTS) {
          this.restartCount++;
          console.log(`Python backend crashed, restarting (${this.restartCount}/${MAX_RESTARTS})...`);
          this.spawnBackend();
        } else {
          this.onErrorCallback?.("Python 后端多次崩溃，已停止重启");
        }
      });
    });
  }

  private getBackendScriptPath(): string {
    const isProd = !process.env.NODE_ENV || process.env.NODE_ENV === "production";
    if (isProd) {
      return path.join(process.resourcesPath, "backend", "main.py");
    }
    return path.join(__dirname, "../../../backend/src/main.py");
  }

  private async waitForHealthCheck(): Promise<void> {
    const start = Date.now();
    return new Promise((resolve, reject) => {
      const check = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:${this.state.port}/health`);
          if (response.ok) {
            resolve();
            return;
          }
        } catch {}
        if (Date.now() - start > HEALTH_CHECK_TIMEOUT) {
          reject(new Error("Health check timeout"));
          return;
        }
        setTimeout(check, HEALTH_CHECK_INTERVAL);
      };
      check();
    });
  }

  async stop(): Promise<void> {
    if (this.state.process) {
      this.state.process.kill("SIGTERM");
      // Wait up to 5 seconds for graceful shutdown
      await new Promise<void>((resolve) => {
        const timeout = setTimeout(() => {
          this.state.process?.kill("SIGKILL");
          resolve();
        }, 5000);
        this.state.process?.on("exit", () => {
          clearTimeout(timeout);
          resolve();
        });
      });
      this.state.process = null;
      this.state.ready = false;
      this.state.port = null;
    }
  }
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd electron && npx tsc --noEmit`
Expected: No errors (or fix import paths)

- [ ] **Step 3: Commit**

```bash
git add electron/src/main/python-manager.ts
git commit -m "feat(bridge): add Python manager with env detection, process lifecycle, health check"
```

---

## Task 2: API Proxy — HTTP + WebSocket

**Files:**
- Create: `electron/src/main/api-proxy.ts`

- [ ] **Step 1: Create API proxy**

```typescript
// electron/src/main/api-proxy.ts
import http from "http";
import { WebSocket, WebSocketServer } from "ws";

export class ApiProxy {
  private httpServer: http.Server | null = null;
  private wss: WebSocketServer | null = null;
  private targetPort: number = 0;

  start(listenPort: number, targetPort: number): void {
    this.targetPort = targetPort;

    this.httpServer = http.createServer((req, res) => {
      const options = {
        hostname: "127.0.0.1",
        port: targetPort,
        path: req.url,
        method: req.method,
        headers: req.headers,
      };

      const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
        proxyRes.pipe(res);
      });

      proxyReq.on("error", (err) => {
        console.error("Proxy error:", err.message);
        res.writeHead(502);
        res.end("Bad Gateway");
      });

      req.pipe(proxyReq);
    });

    this.wss = new WebSocketServer({ server: this.httpServer });
    this.wss.on("connection", (clientWs, req) => {
      const targetWs = new WebSocket(`ws://127.0.0.1:${targetPort}/ws`);

      targetWs.on("open", () => {
        clientWs.on("message", (data) => {
          if (targetWs.readyState === WebSocket.OPEN) {
            targetWs.send(data);
          }
        });
      });

      targetWs.on("message", (data) => {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(data);
        }
      });

      clientWs.on("close", () => {
        targetWs.close();
      });

      targetWs.on("close", () => {
        clientWs.close();
      });

      targetWs.on("error", (err) => {
        console.error("Backend WS error:", err.message);
        clientWs.close();
      });
    });

    this.httpServer.listen(listenPort, "127.0.0.1");
  }

  stop(): void {
    this.wss?.close();
    this.httpServer?.close();
    this.httpServer = null;
    this.wss = null;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add electron/src/main/api-proxy.ts
git commit -m "feat(bridge): add HTTP + WebSocket proxy for backend communication"
```

---

## Task 3: IPC Handlers + Preload Integration

**Files:**
- Create: `electron/src/main/ipc-handlers.ts`
- Modify: `electron/src/main/preload.ts`

- [ ] **Step 1: Create IPC handlers**

```typescript
// electron/src/main/ipc-handlers.ts
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
```

- [ ] **Step 2: Update preload to expose all APIs**

```typescript
// electron/src/main/preload.ts
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
```

- [ ] **Step 3: Commit**

```bash
git add electron/src/main/ipc-handlers.ts electron/src/main/preload.ts
git commit -m "feat(bridge): add IPC handlers and preload API exposure"
```

---

## Task 4: Integrate into Electron Main Process

**Files:**
- Modify: `electron/src/main/index.ts`

- [ ] **Step 1: Update index.ts to use PythonManager and ApiProxy**

```typescript
// electron/src/main/index.ts
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
```

- [ ] **Step 2: Update renderer to connect API client to proxy port**

Update `electron/src/renderer/src/api/client.ts` to receive port from electronAPI:

```typescript
// In client.ts, add initialization function:
export function initApiClient() {
  if (window.electronAPI) {
    window.electronAPI.onBackendReady((port: number) => {
      setBackendPort(port);
    });
  }
}
```

Call `initApiClient()` in `main.ts` after app creation.

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd electron && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add electron/src/
git commit -m "feat(bridge): integrate Python manager, API proxy, and IPC into Electron main process"
```

---

## Task 5: Loading State UI

**Files:**
- Create: `electron/src/renderer/src/components/LoadingScreen.vue`
- Modify: `electron/src/renderer/src/App.vue`

- [ ] **Step 1: Create LoadingScreen component**

```vue
<!-- electron/src/renderer/src/components/LoadingScreen.vue -->
<template>
  <div class="loading-screen">
    <div class="loading-content">
      <el-icon :size="48" class="loading-spinner"><Loading /></el-icon>
      <h2 style="margin-top: 16px">{{ message }}</h2>
      <p v-if="subMessage" style="color: #909399">{{ subMessage }}</p>
      <el-button v-if="showRetry" type="primary" style="margin-top: 16px" @click="$emit('retry')">
        重试
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from "@element-plus/icons-vue";

defineProps<{
  message: string;
  subMessage?: string;
  showRetry?: boolean;
}>();

defineEmits<{ retry: [] }>();
</script>

<style scoped>
.loading-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;
}
.loading-content {
  text-align: center;
}
.loading-spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
```

- [ ] **Step 2: Update App.vue with loading state**

```vue
<!-- electron/src/renderer/src/App.vue -->
<template>
  <LoadingScreen
    v-if="!backendReady"
    :message="loadingMessage"
    :sub-message="loadingError"
    :show-retry="!!loadingError"
    @retry="retryConnection"
  />
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import LoadingScreen from "./components/LoadingScreen.vue";

const backendReady = ref(false);
const loadingMessage = ref("正在初始化...");
const loadingError = ref<string | null>(null);

onMounted(() => {
  if (window.electronAPI) {
    window.electronAPI.onBackendReady((port: number) => {
      backendReady.value = true;
    });
    window.electronAPI.onBackendError((error: string) => {
      loadingError.value = error;
      loadingMessage.value = "启动失败";
    });
  } else {
    // Dev mode without Electron
    backendReady.value = true;
  }

  // Timeout
  setTimeout(() => {
    if (!backendReady.value && !loadingError.value) {
      loadingError.value = "启动超时，请检查 Python 环境";
      loadingMessage.value = "启动失败";
    }
  }, 30000);
});

function retryConnection() {
  loadingError.value = null;
  loadingMessage.value = "正在重试...";
  // Reload the window to retry
  window.location.reload();
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
#app {
  height: 100%;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add loading screen with timeout and retry for backend startup"
```

---

## Task 6: Bridge Integration Smoke Test

**Files:**
- No file changes

- [ ] **Step 1: Start backend separately to verify port output**

Run: `cd backend && python -m src.main`
Expected: `PORT=xxxxx` output, server starts

- [ ] **Step 2: Start Electron in dev mode**

Run: `cd electron && npm run dev`
Expected: Loading screen appears, transitions to main app after backend starts

- [ ] **Step 3: Verify API calls work through proxy**

In renderer dev tools, test: `fetch('/health').then(r => r.json())`
Expected: `{"status":"ok","version":"0.1.0"}`

- [ ] **Step 4: Kill backend process and verify crash recovery**

Kill the Python process, observe Electron detects and restarts it.

- [ ] **Step 5: Commit any fixes**

```bash
git add electron/
git commit -m "fix: address bridge integration issues found during smoke test"
```
