# Youtuber

YouTube 视频下载器 — 基于 Electron + Vue 3 + Python(FastAPI) 的桌面应用。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 / TypeScript / Element Plus / Pinia / Vite |
| 桌面壳 | Electron / electron-builder |
| 后端 | Python 3.10+ / FastAPI / uvicorn / yt-dlp |
| 测试 | Vitest (前端) / pytest (后端) |
| CI/CD | GitHub Actions |

## 项目结构

```
youtuber/
├── backend/                  # Python 后端
│   ├── src/
│   │   ├── api/              # FastAPI 路由 (download, video, playlist, settings, ws)
│   │   ├── core/             # 核心逻辑 (yt-dlp 封装, 下载管理, 进度追踪, URL 检测)
│   │   ├── models/           # Pydantic 数据模型
│   │   ├── config.py         # 配置
│   │   └── main.py           # FastAPI 入口
│   ├── tests/                # pytest 测试
│   ├── requirements.txt
│   └── pyproject.toml
├── electron/                 # Electron 桌面端
│   ├── src/
│   │   ├── main/             # 主进程 (Python 进程管理, API 代理, IPC)
│   │   └── renderer/         # 渲染进程 (Vue 3 应用)
│   │       └── src/
│   │           ├── api/      # 前端 API 调用层
│   │           ├── components/
│   │           ├── views/
│   │           ├── stores/   # Pinia 状态管理
│   │           ├── composables/
│   │           ├── i18n/     # 国际化
│   │           └── router/
│   ├── electron-builder.yml  # 打包配置
│   └── package.json
├── scripts/
│   └── build-backend.py      # PyInstaller 打包后端脚本
├── .github/workflows/        # CI/CD
│   ├── build-windows.yml     # Windows 构建 (手动触发)
│   ├── build-macos.yml       # macOS 构建 (手动触发)
│   └── release.yml           # 发版 (push tag 触发)
└── openspec/                 # 设计规格文档
```

## 环境要求

- **Node.js** >= 20
- **Python** >= 3.10
- **npm**

## 开发

### 1. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd electron
npm install
cd src/renderer
npm install
```

### 2. 启动开发环境

```bash
cd electron
npm run dev
```

这会同时启动：
- Electron 主进程 (TypeScript 编译 + 启动)
- Vue 渲染进程 (Vite dev server, 默认 `http://localhost:5173`)

后端由 Electron 主进程自动管理 (通过 `PythonManager` 启动 Python 子进程)。

### 3. 单独运行后端 (调试用)

```bash
cd backend
python src/main.py
```

后端会在 `127.0.0.1` 上随机端口启动，并输出 `PORT=<端口号>`。

## 测试

```bash
# 前端测试
cd electron
npm run test

# 后端测试
cd backend
pytest
```

## 构建

### 完整构建 (含打包)

```bash
cd electron

# Windows
npm run build:win

# macOS
npm run build:mac
```

这会依次执行：
1. PyInstaller 打包 Python 后端为独立可执行文件
2. Vite 构建 Vue 前端
3. TypeScript 编译 Electron 主进程
4. electron-builder 生成安装包 (Windows: .exe/.msi, macOS: .dmg)

### 分步构建

```bash
# 仅打包后端
npm run build:backend

# 仅构建前端
npm run build:renderer

# 仅编译主进程
npm run build:main
```

构建产物位于 `electron/release/` 目录。

## CI/CD

- **手动构建**: 在 GitHub Actions 中手动触发 `Build Windows` 或 `Build macOS` workflow
- **自动发版**: 推送 `v*` 格式的 tag (如 `v0.1.0`) 会触发 `Release` workflow，自动构建双平台安装包并创建 GitHub Release

```bash
git tag v0.1.0
git push origin v0.1.0
```

## 架构简述

应用启动时，Electron 主进程通过 `PythonManager` 启动 FastAPI 后端子进程，后端随机选择可用端口。主进程启动 `ApiProxy` 将前端请求代理到后端，并通过 WebSocket 推送下载进度。渲染进程使用 Vue 3 + Element Plus 构建 UI，通过 Pinia 管理状态。
