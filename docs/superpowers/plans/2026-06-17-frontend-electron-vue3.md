# Frontend (Electron + Vue3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Electron + Vue3 + Element Plus desktop frontend for the YouTube downloader, including URL input, video info display, format selection, subtitle management, playlist browsing, download queue UI, and settings.

**Architecture:** Electron main process manages Python backend lifecycle and API proxy. Vue3 renderer with Element Plus components, Pinia state management, and WebSocket for real-time updates.

**Tech Stack:** Electron 33+, Vue3, TypeScript, Vite, Element Plus, Pinia, axios, vue-i18n, electron-builder

---

## File Structure

```
electron/
├── src/
│   ├── main/
│   │   ├── index.ts                # Electron app entry, window creation
│   │   ├── python-manager.ts       # Python backend lifecycle management
│   │   ├── ipc-handlers.ts         # IPC handlers for renderer communication
│   │   └── preload.ts              # Preload script (contextBridge)
│   └── renderer/
│       ├── index.html
│       ├── src/
│       │   ├── main.ts             # Vue app entry
│       │   ├── App.vue             # Root component
│       │   ├── router/
│       │   │   └── index.ts        # Vue Router setup
│       │   ├── stores/
│       │   │   ├── video.ts        # Video info store
│       │   │   ├── download.ts     # Download queue store
│       │   │   └── settings.ts     # Settings store
│       │   ├── api/
│       │   │   ├── client.ts       # axios instance
│       │   │   ├── video.ts        # Video API calls
│       │   │   ├── playlist.ts     # Playlist API calls
│       │   │   ├── download.ts     # Download API calls
│       │   │   └── settings.ts     # Settings API calls
│       │   ├── composables/
│       │   │   └── useWebSocket.ts # WebSocket connection composable
│       │   ├── views/
│       │   │   ├── HomeView.vue    # URL input + video info + format/subtitle selection
│       │   │   ├── DownloadView.vue # Download queue with progress
│       │   │   └── SettingsView.vue # Settings panel
│       │   ├── components/
│       │   │   ├── UrlInput.vue    # URL input component
│       │   │   ├── VideoCard.vue   # Video info display card
│       │   │   ├── FormatTable.vue # Format selection table
│       │   │   ├── SubtitleList.vue # Subtitle selection
│       │   │   ├── PlaylistTable.vue # Playlist video list with checkboxes
│       │   │   ├── DownloadItem.vue # Single download task display
│       │   │   └── AppLayout.vue   # Main layout with sidebar
│       │   ├── i18n/
│       │   │   ├── index.ts        # vue-i18n setup
│       │   │   ├── zh.ts           # Chinese translations
│       │   │   └── en.ts           # English translations
│       │   └── types/
│       │       └── index.ts        # TypeScript type definitions
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       └── electron-builder.yml
├── package.json                    # Root package.json for Electron
└── tsconfig.json
```

---

## Task 1: Project Scaffolding — Electron + Vue3 + Vite

**Files:**
- Create: `electron/package.json`
- Create: `electron/tsconfig.json`
- Create: `electron/src/main/index.ts`
- Create: `electron/src/main/preload.ts`
- Create: `electron/src/renderer/package.json`
- Create: `electron/src/renderer/vite.config.ts`
- Create: `electron/src/renderer/tsconfig.json`
- Create: `electron/src/renderer/index.html`
- Create: `electron/src/renderer/src/main.ts`
- Create: `electron/src/renderer/src/App.vue`

- [ ] **Step 1: Create root package.json for Electron**

```json
{
  "name": "youtuber",
  "version": "0.1.0",
  "description": "YouTube Video Downloader",
  "main": "dist/main/index.js",
  "scripts": {
    "dev": "concurrently \"npm run dev:main\" \"npm run dev:renderer\"",
    "dev:main": "tsc -p tsconfig.json && electron .",
    "dev:renderer": "cd src/renderer && npm run dev",
    "build": "npm run build:renderer && npm run build:main && electron-builder",
    "build:main": "tsc -p tsconfig.json",
    "build:renderer": "cd src/renderer && npm run build",
    "test": "cd src/renderer && npm run test"
  },
  "devDependencies": {
    "electron": "^33.0.0",
    "electron-builder": "^25.0.0",
    "typescript": "^5.6.0",
    "concurrently": "^9.0.0"
  }
}
```

- [ ] **Step 2: Create root tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "dist/main",
    "rootDir": "src/main",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/main/**/*"]
}
```

- [ ] **Step 3: Create Electron main process entry**

```typescript
// electron/src/main/index.ts
import { app, BrowserWindow, ipcMain } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
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

app.whenReady().then(createWindow);

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

- [ ] **Step 4: Create preload script**

```typescript
// electron/src/main/preload.ts
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  getBackendPort: () => ipcRenderer.invoke("get-backend-port"),
  onBackendReady: (callback: (port: number) => void) =>
    ipcRenderer.on("backend-ready", (_event, port) => callback(port)),
  onBackendError: (callback: (error: string) => void) =>
    ipcRenderer.on("backend-error", (_event, error) => callback(error)),
});
```

- [ ] **Step 5: Create renderer package.json**

```json
{
  "name": "youtuber-renderer",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0",
    "vue-i18n": "^10.0.0",
    "@element-plus/icons-vue": "^2.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0",
    "@vue/test-utils": "^2.4.0",
    "jsdom": "^25.0.0"
  }
}
```

- [ ] **Step 6: Create vite.config.ts**

```typescript
// electron/src/renderer/vite.config.ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  base: "./",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5173,
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
```

- [ ] **Step 7: Create renderer tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "noEmit": true,
    "skipLibCheck": true,
    "types": ["vite/client"],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 8: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Youtuber</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 9: Create Vue app entry**

```typescript
// electron/src/renderer/src/main.ts
import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ElementPlus);
app.mount("#app");
```

- [ ] **Step 10: Create App.vue**

```vue
<!-- electron/src/renderer/src/App.vue -->
<template>
  <router-view />
</template>

<script setup lang="ts">
</script>
```

- [ ] **Step 11: Install dependencies and verify**

Run: `cd electron && npm install && cd src/renderer && npm install`
Expected: No errors

- [ ] **Step 12: Commit**

```bash
git add electron/
git commit -m "chore: scaffold Electron + Vue3 + Vite project"
```

---

## Task 2: TypeScript Types + API Client

**Files:**
- Create: `electron/src/renderer/src/types/index.ts`
- Create: `electron/src/renderer/src/api/client.ts`

- [ ] **Step 1: Create TypeScript type definitions**

```typescript
// electron/src/renderer/src/types/index.ts
export interface FormatInfo {
  format_id: string;
  ext: string;
  resolution: string;
  fps: number | null;
  vcodec: string;
  acodec: string;
  filesize: number | null;
  format_note: string;
  is_video_only: boolean;
  is_audio_only: boolean;
}

export interface SubtitleInfo {
  language: string;
  language_name: string;
  ext: string;
  is_auto_generated: boolean;
}

export interface VideoInfo {
  id: string;
  title: string;
  duration: number;
  uploader: string;
  thumbnail: string;
  webpage_url: string;
  formats: FormatInfo[];
  subtitles: SubtitleInfo[];
}

export interface PlaylistVideoItem {
  id: string;
  title: string;
  duration: number | null;
  thumbnail: string;
  url: string;
}

export interface PlaylistInfo {
  id: string;
  title: string;
  uploader: string;
  video_count: number;
  videos: PlaylistVideoItem[];
  page: number;
  total_pages: number;
}

export type DownloadStatus =
  | "waiting"
  | "downloading"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled";

export interface DownloadProgress {
  percent: number;
  speed: number;
  downloaded_bytes: number;
  total_bytes: number | null;
  eta: number | null;
}

export interface DownloadTask {
  id: string;
  video_id: string;
  title: string;
  url: string;
  format_id: string;
  status: DownloadStatus;
  progress: DownloadProgress | null;
  filepath: string | null;
  error: string | null;
}

export interface AppSettings {
  download_dir: string;
  default_quality: string;
  proxy: string | null;
  max_concurrent_downloads: number;
  language: string;
}
```

- [ ] **Step 2: Create axios API client**

```typescript
// electron/src/renderer/src/api/client.ts
import axios from "axios";

let _port: number | null = null;

export function setBackendPort(port: number) {
  _port = port;
}

export function getBackendPort(): number {
  if (!_port) throw new Error("Backend port not set");
  return _port;
}

const client = axios.create({
  baseURL: `http://127.0.0.1:${_port}`,
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  if (_port) {
    config.baseURL = `http://127.0.0.1:${_port}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Unknown error";
    return Promise.reject(new Error(message));
  }
);

export default client;
```

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/types/ electron/src/renderer/src/api/client.ts
git commit -m "feat(types): add TypeScript types and axios API client"
```

---

## Task 3: Vue Router + App Layout

**Files:**
- Create: `electron/src/renderer/src/router/index.ts`
- Create: `electron/src/renderer/src/components/AppLayout.vue`
- Create: `electron/src/renderer/src/views/HomeView.vue`
- Create: `electron/src/renderer/src/views/DownloadView.vue`
- Create: `electron/src/renderer/src/views/SettingsView.vue`
- Modify: `electron/src/renderer/src/App.vue`

- [ ] **Step 1: Create router**

```typescript
// electron/src/renderer/src/router/index.ts
import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      component: () => import("../components/AppLayout.vue"),
      children: [
        { path: "", name: "home", component: () => import("../views/HomeView.vue") },
        { path: "downloads", name: "downloads", component: () => import("../views/DownloadView.vue") },
        { path: "settings", name: "settings", component: () => import("../views/SettingsView.vue") },
      ],
    },
  ],
});

export default router;
```

- [ ] **Step 2: Create AppLayout with sidebar**

```vue
<!-- electron/src/renderer/src/components/AppLayout.vue -->
<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background: #304156">
      <div style="padding: 20px; color: #fff; text-align: center; font-size: 18px; font-weight: bold">
        Youtuber
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/">
          <el-icon><VideoPlay /></el-icon>
          <span>视频解析</span>
        </el-menu-item>
        <el-menu-item index="/downloads">
          <el-icon><Download /></el-icon>
          <span>下载管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { VideoPlay, Download, Setting } from "@element-plus/icons-vue";

const route = useRoute();
const activeMenu = computed(() => route.path);
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
</style>
```

- [ ] **Step 3: Create placeholder views**

```vue
<!-- electron/src/renderer/src/views/HomeView.vue -->
<template>
  <div>
    <h2>视频解析</h2>
    <p>在此输入 YouTube URL 进行解析</p>
  </div>
</template>

<script setup lang="ts">
</script>
```

```vue
<!-- electron/src/renderer/src/views/DownloadView.vue -->
<template>
  <div>
    <h2>下载管理</h2>
    <p>下载队列将在此显示</p>
  </div>
</template>

<script setup lang="ts">
</script>
```

```vue
<!-- electron/src/renderer/src/views/SettingsView.vue -->
<template>
  <div>
    <h2>设置</h2>
    <p>应用设置将在此显示</p>
  </div>
</template>

<script setup lang="ts">
</script>
```

- [ ] **Step 4: Update App.vue**

```vue
<!-- electron/src/renderer/src/App.vue -->
<template>
  <router-view />
</template>

<script setup lang="ts">
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

- [ ] **Step 5: Verify app renders**

Run: `cd electron/src/renderer && npm run dev`
Expected: Browser shows sidebar with navigation, clicking routes works

- [ ] **Step 6: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add Vue Router, AppLayout with sidebar navigation"
```

---

## Task 4: Pinia Stores + i18n Setup

**Files:**
- Create: `electron/src/renderer/src/stores/video.ts`
- Create: `electron/src/renderer/src/stores/download.ts`
- Create: `electron/src/renderer/src/stores/settings.ts`
- Create: `electron/src/renderer/src/i18n/index.ts`
- Create: `electron/src/renderer/src/i18n/zh.ts`
- Create: `electron/src/renderer/src/i18n/en.ts`

- [ ] **Step 1: Create video store**

```typescript
// electron/src/renderer/src/stores/video.ts
import { defineStore } from "pinia";
import { ref } from "vue";
import type { VideoInfo, PlaylistInfo } from "@/types";

export const useVideoStore = defineStore("video", () => {
  const currentVideo = ref<VideoInfo | null>(null);
  const currentPlaylist = ref<PlaylistInfo | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  function setVideo(info: VideoInfo) {
    currentVideo.value = info;
    currentPlaylist.value = null;
    error.value = null;
  }

  function setPlaylist(info: PlaylistInfo) {
    currentPlaylist.value = info;
    currentVideo.value = null;
    error.value = null;
  }

  function setLoading(v: boolean) {
    loading.value = v;
  }

  function setError(msg: string | null) {
    error.value = msg;
  }

  function clear() {
    currentVideo.value = null;
    currentPlaylist.value = null;
    error.value = null;
  }

  return {
    currentVideo,
    currentPlaylist,
    loading,
    error,
    setVideo,
    setPlaylist,
    setLoading,
    setError,
    clear,
  };
});
```

- [ ] **Step 2: Create download store**

```typescript
// electron/src/renderer/src/stores/download.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { DownloadTask } from "@/types";

export const useDownloadStore = defineStore("download", () => {
  const tasks = ref<DownloadTask[]>([]);

  const waitingTasks = computed(() => tasks.value.filter((t) => t.status === "waiting"));
  const activeTasks = computed(() => tasks.value.filter((t) => t.status === "downloading"));
  const completedTasks = computed(() => tasks.value.filter((t) => t.status === "completed"));

  function addTask(task: DownloadTask) {
    tasks.value.push(task);
  }

  function updateTask(taskId: string, updates: Partial<DownloadTask>) {
    const idx = tasks.value.findIndex((t) => t.id === taskId);
    if (idx !== -1) {
      tasks.value[idx] = { ...tasks.value[idx], ...updates };
    }
  }

  function removeTask(taskId: string) {
    tasks.value = tasks.value.filter((t) => t.id !== taskId);
  }

  function updateProgress(taskId: string, progress: DownloadTask["progress"]) {
    const idx = tasks.value.findIndex((t) => t.id === taskId);
    if (idx !== -1) {
      tasks.value[idx].progress = progress;
    }
  }

  function setTasks(newTasks: DownloadTask[]) {
    tasks.value = newTasks;
  }

  return {
    tasks,
    waitingTasks,
    activeTasks,
    completedTasks,
    addTask,
    updateTask,
    removeTask,
    updateProgress,
    setTasks,
  };
});
```

- [ ] **Step 3: Create settings store**

```typescript
// electron/src/renderer/src/stores/settings.ts
import { defineStore } from "pinia";
import { ref } from "vue";
import type { AppSettings } from "@/types";

export const useSettingsStore = defineStore("settings", () => {
  const settings = ref<AppSettings>({
    download_dir: "",
    default_quality: "best",
    proxy: null,
    max_concurrent_downloads: 3,
    language: "zh",
  });

  function setSettings(newSettings: AppSettings) {
    settings.value = newSettings;
  }

  function updateSettings(partial: Partial<AppSettings>) {
    settings.value = { ...settings.value, ...partial };
  }

  return { settings, setSettings, updateSettings };
});
```

- [ ] **Step 4: Create i18n translations**

```typescript
// electron/src/renderer/src/i18n/zh.ts
export default {
  nav: {
    home: "视频解析",
    downloads: "下载管理",
    settings: "设置",
  },
  home: {
    title: "视频解析",
    urlPlaceholder: "请输入 YouTube 视频/播放列表/频道 URL",
    parse: "解析",
    parsing: "解析中...",
  },
  download: {
    title: "下载管理",
    start: "开始下载",
    pause: "暂停",
    resume: "恢复",
    cancel: "取消",
    remove: "移除",
    completed: "已完成",
    failed: "失败",
    waiting: "等待中",
    downloading: "下载中",
    paused: "已暂停",
    speed: "速度",
    eta: "剩余时间",
    noDownloads: "暂无下载任务",
  },
  settings: {
    title: "设置",
    downloadDir: "下载目录",
    defaultQuality: "默认画质",
    proxy: "代理设置",
    maxConcurrent: "最大并发下载数",
    language: "语言",
    save: "保存",
    saved: "设置已保存",
  },
};
```

```typescript
// electron/src/renderer/src/i18n/en.ts
export default {
  nav: {
    home: "Video",
    downloads: "Downloads",
    settings: "Settings",
  },
  home: {
    title: "Video Parser",
    urlPlaceholder: "Enter YouTube video/playlist/channel URL",
    parse: "Parse",
    parsing: "Parsing...",
  },
  download: {
    title: "Downloads",
    start: "Start",
    pause: "Pause",
    resume: "Resume",
    cancel: "Cancel",
    remove: "Remove",
    completed: "Completed",
    failed: "Failed",
    waiting: "Waiting",
    downloading: "Downloading",
    paused: "Paused",
    speed: "Speed",
    eta: "ETA",
    noDownloads: "No download tasks",
  },
  settings: {
    title: "Settings",
    downloadDir: "Download Directory",
    defaultQuality: "Default Quality",
    proxy: "Proxy",
    maxConcurrent: "Max Concurrent Downloads",
    language: "Language",
    save: "Save",
    saved: "Settings saved",
  },
};
```

```typescript
// electron/src/renderer/src/i18n/index.ts
import { createI18n } from "vue-i18n";
import zh from "./zh";
import en from "./en";

const i18n = createI18n({
  legacy: false,
  locale: "zh",
  fallbackLocale: "en",
  messages: { zh, en },
});

export default i18n;
```

- [ ] **Step 5: Update main.ts to use i18n**

Update `electron/src/renderer/src/main.ts` to add `app.use(i18n)`.

- [ ] **Step 6: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(stores): add Pinia stores for video/download/settings and i18n setup"
```

---

## Task 5: API Modules + WebSocket Composable

**Files:**
- Create: `electron/src/renderer/src/api/video.ts`
- Create: `electron/src/renderer/src/api/playlist.ts`
- Create: `electron/src/renderer/src/api/download.ts`
- Create: `electron/src/renderer/src/api/settings.ts`
- Create: `electron/src/renderer/src/composables/useWebSocket.ts`

- [ ] **Step 1: Create video API**

```typescript
// electron/src/renderer/src/api/video.ts
import client from "./client";
import type { VideoInfo } from "@/types";

export async function getVideoInfo(url: string): Promise<VideoInfo> {
  const { data } = await client.post("/api/v1/video/info", { url });
  return data;
}
```

- [ ] **Step 2: Create playlist API**

```typescript
// electron/src/renderer/src/api/playlist.ts
import client from "./client";
import type { PlaylistInfo } from "@/types";

export async function getPlaylistInfo(
  url: string,
  page = 1,
  pageSize = 50
): Promise<PlaylistInfo> {
  const { data } = await client.post("/api/v1/playlist/info", {
    url,
    page,
    page_size: pageSize,
  });
  return data;
}
```

- [ ] **Step 3: Create download API**

```typescript
// electron/src/renderer/src/api/download.ts
import client from "./client";
import type { DownloadTask } from "@/types";

export async function startDownload(
  url: string,
  videoId: string,
  title: string,
  formatId: string
): Promise<DownloadTask> {
  const { data } = await client.post("/api/v1/download", {
    url,
    video_id: videoId,
    title,
    format_id: formatId,
  });
  return data;
}

export async function getDownloadQueue(): Promise<DownloadTask[]> {
  const { data } = await client.get("/api/v1/download/queue");
  return data;
}

export async function pauseDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/pause`);
  return data;
}

export async function resumeDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/resume`);
  return data;
}

export async function cancelDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/cancel`);
  return data;
}
```

- [ ] **Step 4: Create settings API**

```typescript
// electron/src/renderer/src/api/settings.ts
import client from "./client";
import type { AppSettings } from "@/types";

export async function getSettings(): Promise<AppSettings> {
  const { data } = await client.get("/api/v1/settings");
  return data;
}

export async function updateSettings(
  partial: Partial<AppSettings>
): Promise<AppSettings> {
  const { data } = await client.put("/api/v1/settings", partial);
  return data;
}
```

- [ ] **Step 5: Create WebSocket composable**

```typescript
// electron/src/renderer/src/composables/useWebSocket.ts
import { ref, onUnmounted } from "vue";
import { getBackendPort } from "@/api/client";

export function useWebSocket() {
  const connected = ref(false);
  const ws = ref<WebSocket | null>(null);
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  function connect(onMessage: (data: any) => void) {
    const port = getBackendPort();
    const socket = new WebSocket(`ws://127.0.0.1:${port}/ws`);

    socket.onopen = () => {
      connected.value = true;
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {}
    };

    socket.onclose = () => {
      connected.value = false;
      reconnectTimer = setTimeout(() => connect(onMessage), 3000);
    };

    socket.onerror = () => {
      socket.close();
    };

    ws.value = socket;
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (ws.value) {
      ws.value.close();
      ws.value = null;
    }
  }

  onUnmounted(disconnect);

  return { connected, connect, disconnect };
}
```

- [ ] **Step 6: Commit**

```bash
git add electron/src/renderer/src/api/ electron/src/renderer/src/composables/
git commit -m "feat(api): add API modules for video/playlist/download/settings and WebSocket composable"
```

---

## Task 6: HomeView — URL Input + Video Info Display

**Files:**
- Create: `electron/src/renderer/src/components/UrlInput.vue`
- Create: `electron/src/renderer/src/components/VideoCard.vue`
- Modify: `electron/src/renderer/src/views/HomeView.vue`

- [ ] **Step 1: Create UrlInput component**

```vue
<!-- electron/src/renderer/src/components/UrlInput.vue -->
<template>
  <div style="display: flex; gap: 12px">
    <el-input
      v-model="url"
      :placeholder="t('home.urlPlaceholder')"
      size="large"
      clearable
      @keyup.enter="onParse"
    />
    <el-button type="primary" size="large" :loading="loading" @click="onParse">
      {{ loading ? t('home.parsing') : t('home.parse') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

defineProps<{ loading: boolean }>();
const emit = defineEmits<{ parse: [url: string] }>();

const url = ref("");

function onParse() {
  if (url.value.trim()) {
    emit("parse", url.value.trim());
  }
}
</script>
```

- [ ] **Step 2: Create VideoCard component**

```vue
<!-- electron/src/renderer/src/components/VideoCard.vue -->
<template>
  <el-card v-if="video" style="margin-top: 16px">
    <div style="display: flex; gap: 16px">
      <img
        :src="video.thumbnail"
        :alt="video.title"
        style="width: 320px; height: 180px; object-fit: cover; border-radius: 8px"
      />
      <div>
        <h3 style="margin: 0 0 8px 0">{{ video.title }}</h3>
        <p style="color: #909399; margin: 0 0 4px 0">
          {{ video.uploader }} · {{ formatDuration(video.duration) }}
        </p>
        <p style="color: #909399; margin: 0; font-size: 12px">
          {{ video.formats.length }} 个格式 · {{ video.subtitles.length }} 个字幕
        </p>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { VideoInfo } from "@/types";

defineProps<{ video: VideoInfo }>();

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
</script>
```

- [ ] **Step 3: Update HomeView**

```vue
<!-- electron/src/renderer/src/views/HomeView.vue -->
<template>
  <div>
    <h2>{{ t('home.title') }}</h2>
    <UrlInput :loading="videoStore.loading" @parse="handleParse" />
    <VideoCard v-if="videoStore.currentVideo" :video="videoStore.currentVideo" />
    <el-alert
      v-if="videoStore.error"
      :title="videoStore.error"
      type="error"
      show-icon
      style="margin-top: 16px"
      closable
      @close="videoStore.setError(null)"
    />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useVideoStore } from "@/stores/video";
import { getVideoInfo } from "@/api/video";
import { getPlaylistInfo } from "@/api/playlist";
import UrlInput from "@/components/UrlInput.vue";
import VideoCard from "@/components/VideoCard.vue";

const { t } = useI18n();
const videoStore = useVideoStore();

async function handleParse(url: string) {
  videoStore.setLoading(true);
  videoStore.clear();
  try {
    // Try video info first
    const info = await getVideoInfo(url);
    videoStore.setVideo(info);
  } catch (e: any) {
    videoStore.setError(e.message || "解析失败");
  } finally {
    videoStore.setLoading(false);
  }
}
</script>
```

- [ ] **Step 4: Verify UI renders**

Run: `cd electron/src/renderer && npm run dev`
Expected: URL input renders, sidebar navigation works

- [ ] **Step 5: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add URL input and video card components for HomeView"
```

---

## Task 7: FormatTable + SubtitleList Components

**Files:**
- Create: `electron/src/renderer/src/components/FormatTable.vue`
- Create: `electron/src/renderer/src/components/SubtitleList.vue`
- Modify: `electron/src/renderer/src/views/HomeView.vue`

- [ ] **Step 1: Create FormatTable**

```vue
<!-- electron/src/renderer/src/components/FormatTable.vue -->
<template>
  <div style="margin-top: 16px">
    <h3>可用格式</h3>
    <el-table :data="formats" stripe style="width: 100%" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="format_note" label="清晰度" width="120" />
      <el-table-column prop="resolution" label="分辨率" width="140" />
      <el-table-column prop="ext" label="格式" width="80" />
      <el-table-column prop="fps" label="帧率" width="80">
        <template #default="{ row }">
          {{ row.fps ? `${row.fps}fps` : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="大小" width="120">
        <template #default="{ row }">
          {{ row.filesize ? formatSize(row.filesize) : '未知' }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_video_only" type="warning" size="small">仅视频</el-tag>
          <el-tag v-else-if="row.is_audio_only" type="success" size="small">仅音频</el-tag>
          <el-tag v-else type="info" size="small">合并</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { FormatInfo } from "@/types";

defineProps<{ formats: FormatInfo[] }>();
const emit = defineEmits<{ select: [formats: FormatInfo[]] }>();

const selected = ref<FormatInfo[]>([]);

function onSelectionChange(val: FormatInfo[]) {
  selected.value = val;
  emit("select", val);
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}
</script>
```

- [ ] **Step 2: Create SubtitleList**

```vue
<!-- electron/src/renderer/src/components/SubtitleList.vue -->
<template>
  <div v-if="subtitles.length > 0" style="margin-top: 16px">
    <h3>可用字幕</h3>
    <el-checkbox-group v-model="selectedLanguages">
      <div v-for="sub in subtitles" :key="sub.language" style="margin-bottom: 8px">
        <el-checkbox :value="sub.language" :label="sub.language">
          {{ sub.language_name }}
          <el-tag v-if="sub.is_auto_generated" size="small" type="info">自动</el-tag>
          <el-tag v-else size="small">手动</el-tag>
          ({{ sub.ext }})
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <el-button
      v-if="selectedLanguages.length > 0"
      type="primary"
      size="small"
      style="margin-top: 8px"
      @click="onDownload"
    >
      下载选中字幕
    </el-button>
  </div>
  <el-empty v-else description="无可用字幕" />
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { SubtitleInfo } from "@/types";

defineProps<{ subtitles: SubtitleInfo[] }>();
const emit = defineEmits<{ download: [languages: string[]] }>();

const selectedLanguages = ref<string[]>([]);

function onDownload() {
  emit("download", selectedLanguages.value);
}
</script>
```

- [ ] **Step 3: Update HomeView to include format/subtitle components**

Update HomeView to add FormatTable and SubtitleList below VideoCard when video info is loaded.

- [ ] **Step 4: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add FormatTable and SubtitleList components"
```

---

## Task 8: PlaylistTable Component

**Files:**
- Create: `electron/src/renderer/src/components/PlaylistTable.vue`
- Modify: `electron/src/renderer/src/views/HomeView.vue`

- [ ] **Step 1: Create PlaylistTable**

```vue
<!-- electron/src/renderer/src/components/PlaylistTable.vue -->
<template>
  <div style="margin-top: 16px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
      <h3>{{ playlist.title }} ({{ playlist.video_count }} 个视频)</h3>
      <div>
        <el-button size="small" @click="toggleAll">
          {{ allSelected ? '取消全选' : '全选' }}
        </el-button>
        <el-button type="primary" size="small" :disabled="selectedIds.size === 0" @click="onBatchDownload">
          下载选中 ({{ selectedIds.size }})
        </el-button>
      </div>
    </div>
    <el-table :data="playlist.videos" stripe style="width: 100%" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column label="缩略图" width="120">
        <template #default="{ row }">
          <img :src="row.thumbnail" :alt="row.title" style="width: 100px; height: 56px; object-fit: cover; border-radius: 4px" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column label="时长" width="100">
        <template #default="{ row }">
          {{ row.duration ? formatDuration(row.duration) : '-' }}
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="playlist.total_pages > 1"
      :current-page="playlist.page"
      :page-size="50"
      :total="playlist.video_count"
      layout="prev, pager, next"
      style="margin-top: 16px; justify-content: center"
      @current-change="onPageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { PlaylistInfo, PlaylistVideoItem } from "@/types";

const props = defineProps<{ playlist: PlaylistInfo }>();
const emit = defineEmits<{
  download: [videos: PlaylistVideoItem[]];
  pageChange: [page: number];
}>();

const selectedItems = ref<PlaylistVideoItem[]>([]);
const selectedIds = computed(() => new Set(selectedItems.value.map((v) => v.id)));
const allSelected = computed(() => selectedIds.value.size === props.playlist.videos.length);

function onSelectionChange(items: PlaylistVideoItem[]) {
  selectedItems.value = items;
}

function toggleAll() {
  // Handled by el-table's select-all behavior
}

function onBatchDownload() {
  emit("download", selectedItems.value);
}

function onPageChange(page: number) {
  emit("pageChange", page);
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
</script>
```

- [ ] **Step 2: Update HomeView to handle playlist URLs**

Update HomeView to detect playlist URLs and show PlaylistTable instead of VideoCard when appropriate.

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add PlaylistTable with batch selection and pagination"
```

---

## Task 9: DownloadView — Download Queue UI

**Files:**
- Create: `electron/src/renderer/src/components/DownloadItem.vue`
- Modify: `electron/src/renderer/src/views/DownloadView.vue`

- [ ] **Step 1: Create DownloadItem component**

```vue
<!-- electron/src/renderer/src/components/DownloadItem.vue -->
<template>
  <el-card style="margin-bottom: 12px">
    <div style="display: flex; justify-content: space-between; align-items: center">
      <div style="flex: 1">
        <h4 style="margin: 0 0 4px 0">{{ task.title }}</h4>
        <div style="display: flex; gap: 12px; align-items: center">
          <el-tag :type="statusType" size="small">{{ statusText }}</el-tag>
          <span v-if="task.progress" style="color: #909399; font-size: 12px">
            {{ formatSpeed(task.progress.speed) }} · {{ formatEta(task.progress.eta) }}
          </span>
        </div>
        <el-progress
          v-if="task.status === 'downloading' && task.progress"
          :percentage="Math.round(task.progress.percent)"
          :stroke-width="8"
          style="margin-top: 8px"
        />
        <p v-if="task.error" style="color: #f56c6c; font-size: 12px; margin: 4px 0 0 0">
          {{ task.error }}
        </p>
        <p v-if="task.filepath" style="color: #67c23a; font-size: 12px; margin: 4px 0 0 0">
          {{ task.filepath }}
        </p>
      </div>
      <div style="display: flex; gap: 8px">
        <el-button v-if="task.status === 'downloading'" size="small" @click="$emit('pause', task.id)">
          暂停
        </el-button>
        <el-button v-if="task.status === 'paused'" size="small" type="primary" @click="$emit('resume', task.id)">
          恢复
        </el-button>
        <el-button
          v-if="task.status === 'waiting' || task.status === 'downloading' || task.status === 'paused'"
          size="small"
          type="danger"
          @click="$emit('cancel', task.id)"
        >
          取消
        </el-button>
        <el-button
          v-if="task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled'"
          size="small"
          @click="$emit('remove', task.id)"
        >
          移除
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { DownloadTask } from "@/types";

const props = defineProps<{ task: DownloadTask }>();
defineEmits<{
  pause: [id: string];
  resume: [id: string];
  cancel: [id: string];
  remove: [id: string];
}>();

const statusType = computed(() => {
  const map: Record<string, string> = {
    waiting: "info",
    downloading: "",
    paused: "warning",
    completed: "success",
    failed: "danger",
    cancelled: "info",
  };
  return map[props.task.status] || "info";
});

const statusText = computed(() => {
  const map: Record<string, string> = {
    waiting: "等待中",
    downloading: "下载中",
    paused: "已暂停",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
  };
  return map[props.task.status] || props.task.status;
});

function formatSpeed(bytesPerSec: number): string {
  if (bytesPerSec < 1024 * 1024) return `${(bytesPerSec / 1024).toFixed(0)} KB/s`;
  return `${(bytesPerSec / 1024 / 1024).toFixed(1)} MB/s`;
}

function formatEta(seconds: number | null): string {
  if (!seconds) return "";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `剩余 ${m}:${s.toString().padStart(2, "0")}`;
}
</script>
```

- [ ] **Step 2: Update DownloadView**

```vue
<!-- electron/src/renderer/src/views/DownloadView.vue -->
<template>
  <div>
    <h2>{{ t('download.title') }}</h2>
    <div v-if="downloadStore.tasks.length === 0">
      <el-empty :description="t('download.noDownloads')" />
    </div>
    <DownloadItem
      v-for="task in downloadStore.tasks"
      :key="task.id"
      :task="task"
      @pause="handlePause"
      @resume="handleResume"
      @cancel="handleCancel"
      @remove="handleRemove"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { useDownloadStore } from "@/stores/download";
import { getDownloadQueue, pauseDownload, resumeDownload, cancelDownload } from "@/api/download";
import { useWebSocket } from "@/composables/useWebSocket";
import DownloadItem from "@/components/DownloadItem.vue";

const { t } = useI18n();
const downloadStore = useDownloadStore();
const { connect, disconnect } = useWebSocket();

onMounted(async () => {
  try {
    const tasks = await getDownloadQueue();
    downloadStore.setTasks(tasks);
  } catch {}

  connect((data) => {
    if (data.task_id && data.progress) {
      downloadStore.updateProgress(data.task_id, data.progress);
    }
    if (data.task_id && data.status) {
      downloadStore.updateTask(data.task_id, { status: data.status });
    }
  });
});

onUnmounted(() => {
  disconnect();
});

async function handlePause(id: string) {
  try {
    const task = await pauseDownload(id);
    downloadStore.updateTask(id, task);
  } catch {}
}

async function handleResume(id: string) {
  try {
    const task = await resumeDownload(id);
    downloadStore.updateTask(id, task);
  } catch {}
}

async function handleCancel(id: string) {
  try {
    await cancelDownload(id);
    downloadStore.removeTask(id);
  } catch {}
}

function handleRemove(id: string) {
  downloadStore.removeTask(id);
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(ui): add DownloadView with progress, pause/resume/cancel controls"
```

---

## Task 10: SettingsView

**Files:**
- Modify: `electron/src/renderer/src/views/SettingsView.vue`

- [ ] **Step 1: Implement SettingsView**

```vue
<!-- electron/src/renderer/src/views/SettingsView.vue -->
<template>
  <div>
    <h2>{{ t('settings.title') }}</h2>
    <el-form label-width="160px" style="max-width: 600px">
      <el-form-item :label="t('settings.downloadDir')">
        <el-input v-model="form.download_dir" />
      </el-form-item>
      <el-form-item :label="t('settings.defaultQuality')">
        <el-select v-model="form.default_quality" style="width: 100%">
          <el-option label="最高画质" value="best" />
          <el-option label="1080p" value="1080p" />
          <el-option label="720p" value="720p" />
          <el-option label="仅音频" value="audio" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('settings.proxy')">
        <el-input v-model="form.proxy" placeholder="http://127.0.0.1:7890" clearable />
      </el-form-item>
      <el-form-item :label="t('settings.maxConcurrent')">
        <el-input-number v-model="form.max_concurrent_downloads" :min="1" :max="10" />
      </el-form-item>
      <el-form-item :label="t('settings.language')">
        <el-select v-model="form.language" style="width: 100%" @change="onLanguageChange">
          <el-option label="中文" value="zh" />
          <el-option label="English" value="en" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSave">{{ t('settings.save') }}</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { useSettingsStore } from "@/stores/settings";
import { getSettings, updateSettings } from "@/api/settings";
import type { AppSettings } from "@/types";

const { t, locale } = useI18n();
const settingsStore = useSettingsStore();

const form = ref<AppSettings>({
  download_dir: "",
  default_quality: "best",
  proxy: null,
  max_concurrent_downloads: 3,
  language: "zh",
});

onMounted(async () => {
  try {
    const settings = await getSettings();
    settingsStore.setSettings(settings);
    form.value = { ...settings };
  } catch {}
});

function onLanguageChange(lang: string) {
  locale.value = lang;
}

async function onSave() {
  try {
    const updated = await updateSettings(form.value);
    settingsStore.setSettings(updated);
    locale.value = updated.language;
    ElMessage.success(t('settings.saved'));
  } catch (e: any) {
    ElMessage.error(e.message || "保存失败");
  }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add electron/src/renderer/src/views/SettingsView.vue
git commit -m "feat(ui): add SettingsView with form, language switching, persistence"
```

---

## Task 11: i18n Integration into Components

**Files:**
- Modify: all view and component files using hardcoded Chinese text

- [ ] **Step 1: Update all components to use `t()` for user-facing text**

Replace all hardcoded Chinese strings in FormatTable, SubtitleList, PlaylistTable, DownloadItem, AppLayout with `t('key')` calls.

- [ ] **Step 2: Add missing translation keys to zh.ts and en.ts**

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/
git commit -m "feat(i18n): replace hardcoded strings with i18n translation keys"
```

---

## Task 12: Full Frontend Build + Smoke Test

**Files:**
- No new files

- [ ] **Step 1: Run TypeScript type check**

Run: `cd electron/src/renderer && npx vue-tsc --noEmit`
Expected: No type errors

- [ ] **Step 2: Run Vite build**

Run: `cd electron/src/renderer && npm run build`
Expected: Build succeeds, dist/ directory created

- [ ] **Step 3: Run dev server and verify all pages**

Run: `cd electron/src/renderer && npm run dev`
Expected: All three views render correctly

- [ ] **Step 4: Fix any build/type errors**

- [ ] **Step 5: Commit**

```bash
git add electron/
git commit -m "fix: resolve build issues and verify frontend compiles"
```
