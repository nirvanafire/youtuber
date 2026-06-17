## Context

构建一个自用的 YouTube 视频下载桌面应用。核心技术栈已确认：Electron + Vue3 + Element Plus 前端，FastAPI + yt-dlp Python 后端。项目从零开始，无历史代码约束。

yt-dlp 是 youtube-dl 的活跃 fork（171k stars，2026.06.09 最新发布），支持 941 个网站提取器，提供 Python 库模式调用，可通过 `extract_info()` 获取结构化视频数据，通过 `progress_hooks` 获取下载进度。

## Goals / Non-Goals

**Goals:**
- 提供现代桌面 GUI，替代 yt-dlp 命令行操作
- 支持视频信息解析、格式选择、字幕下载、播放列表浏览、下载队列管理
- 实时显示下载进度（WebSocket 推送）
- 打包为独立桌面应用，Windows 和 macOS 可用
- 通过 GitHub Actions 自动构建和发布

**Non-Goals:**
- 不支持视频在线播放/预览
- 不支持视频编辑或转码（仅下载）
- 不实现用户账号登录/YouTube OAuth
- 不支持移动端（仅桌面端）
- 不做插件系统或扩展机制
- 初期不支持除 YouTube 以外的网站（虽然后端抽象可扩展）

## Decisions

### D1: 前后端通信 — REST + WebSocket 混合

**选择**: REST API 用于请求-响应操作，WebSocket 用于实时进度推送

**理由**: 下载进度是高频单向推送场景（每秒多次更新），WebSocket 比 REST 轮询高效得多。其他操作（获取视频信息、触发下载、管理设置）是标准的请求-响应模式，REST 更简单直观。

**替代方案**:
- 纯 REST + 轮询：简单但浪费带宽，进度更新延迟高
- gRPC：性能好但前端集成复杂，浏览器不原生支持
- stdin/stdout JSON：调试困难，不适合复杂 API

### D2: yt-dlp 调用方式 — Python 库模式

**选择**: `import yt_dlp`，使用 `YoutubeDL` 类的 Python API

**理由**: 库模式可获取结构化的视频元数据（格式列表、字幕列表、缩略图 URL 等），支持 `progress_hooks` 回调实现实时进度，支持 `extract_info(url, download=False)` 先预览再下载。CLI 子进程模式只能解析文本输出，丢失结构化数据。

**替代方案**:
- subprocess 调用 yt-dlp CLI：简单但无法获取结构化数据，进度解析脆弱

### D3: Electron 与 Python 进程管理

**选择**: Electron main process 作为 Python 后端的生命周期管理器

**流程**:
1. Electron 启动时检测用户环境是否有 Python 3.10+
2. 有 → 使用用户 Python 启动 FastAPI
3. 无 → 使用内嵌的便携版 Python
4. 通过随机端口启动 FastAPI，健康检查通过后通知渲染进程
5. Electron 退出时优雅关闭 Python 进程

**理由**: 自用场景优先使用用户环境减少包体积；内嵌便携版保证零配置可用。

### D4: 前端状态管理 — Pinia

**选择**: Pinia（Vue3 官方推荐的状态管理库）

**理由**: Vue3 生态标准，TypeScript 支持好，DevTools 集成完善。适合管理下载队列状态、视频信息缓存、设置等全局状态。

**替代方案**:
- Vuex：Vue2 时代的方案，对 Vue3 支持不如 Pinia
- 纯 composables：适合小型应用，下载队列管理需要集中状态

### D5: UI 组件库 — Element Plus

**选择**: Element Plus

**理由**: Vue3 生态最大的组件库，组件覆盖面全（表格、表单、对话框、通知、进度条等），中文文档完善，社区资源丰富。

**替代方案**:
- Naive UI：设计更现代，TypeScript 原生，但生态和资料较少
- Vuetify：Vue3 版本成熟度不如 Element Plus

### D6: 打包策略

**前端**: electron-builder 打包 Electron 应用，将 Python 后端可执行文件作为 extraResources 嵌入

**后端**: PyInstaller `--onefile` 模式打包 Python 后端为单个可执行文件

**流程**:
1. GitHub Actions Job 1: PyInstaller 打包 Python → `backend.exe` (Win) / `backend` (Mac)
2. GitHub Actions Job 2: electron-builder 打包前端，将 Job 1 产物嵌入
3. 输出: `.exe` + `.msi` (Windows), `.dmg` (macOS)

**理由**: PyInstaller 产物独立运行不依赖 Python 环境；electron-builder 成熟稳定，支持自动更新。

### D7: API 端口策略

**选择**: Electron 启动 Python 后端时随机选择可用端口（10000-60000 范围）

**理由**: 避免与用户其他服务端口冲突。端口号通过 stdout 传递给 Electron 主进程。

**替代方案**:
- 固定端口：简单但可能冲突
- Unix socket/Named pipe：跨平台兼容性差

## Risks / Trade-offs

**[R1] yt-dlp 更新频率高，API 可能变化** → 使用 yt-dlp 的稳定公开 API（`YoutubeDL` 类、`extract_info`、`progress_hooks`），这些是长期稳定的接口。后端封装隔离变化。

**[R2] PyInstaller 打包体积大（100-150MB）** → 可通过 `--exclude-module` 排除不需要的模块减小体积。自用场景可接受。

**[R3] YouTube 反爬机制（PO Token、验证码）** → yt-dlp 持续跟进反爬策略。支持 `--cookies-from-browser` 利用用户已登录的浏览器 cookie。初期不做自动化验证码处理。

**[R4] Python 启动时间可能较慢（2-5秒）** → Electron 显示 loading 界面等待健康检查。后续可考虑 Python 后台常驻或 uvicorn 多 worker。

**[R5] 跨平台构建复杂度** → GitHub Actions 矩阵构建隔离环境。Windows 和 macOS 分别独立 job，避免交叉编译问题。

## Open Questions

- **O1**: 是否需要支持下载断点续传？（yt-dlp 支持 `--continue`，但需要后端队列管理配合）
- **O2**: 下载文件的命名规则和目录结构如何设计？（按播放列表分文件夹？自定义模板？）
- **O3**: 是否需要代理设置的自动检测（系统代理）？
