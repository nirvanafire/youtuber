## 1. 项目初始化与基础架构

- [ ] 1.1 初始化项目根目录结构（electron/、backend/、.github/workflows/、scripts/）
- [ ] 1.2 创建 Python 后端项目：FastAPI 骨架、requirements.txt、项目结构（src/api/、src/core/、src/models/）
- [ ] 1.3 创建 Electron + Vue3 前端项目：使用 Vite + TypeScript 初始化，配置 Element Plus、Pinia
- [ ] 1.4 配置 Electron 主进程基础框架（窗口创建、preload 脚本）
- [ ] 1.5 实现 Python 后端健康检查端点 GET /health

## 2. Electron-Python 桥接层

- [ ] 2.1 实现 Python 环境检测：扫描用户机器上的 Python 3.10+（python-manager.ts）
- [ ] 2.2 实现 Python 子进程启动：随机端口分配、stdout 端口读取、进程生命周期管理
- [ ] 2.3 实现后端崩溃检测与自动重启（最多 3 次重试）
- [ ] 2.4 实现 API 代理：主进程将渲染进程的 REST 请求转发到 Python 后端
- [ ] 2.5 实现 WebSocket 代理：主进程将渲染进程的 WebSocket 连接代理到后端
- [ ] 2.6 实现前端 Loading 状态：后端启动期间显示加载动画，超时 30 秒显示错误提示

## 3. 后端核心：yt-dlp 封装

- [ ] 3.1 实现 yt-dlp 封装层（ytdl_wrapper.py）：extract_info 获取视频元数据
- [ ] 3.2 实现 URL 类型识别：区分单视频、播放列表、频道、短视频
- [ ] 3.3 实现格式列表提取：解析所有可用视频/音频格式（分辨率、编码、大小、帧率）
- [ ] 3.4 实现字幕列表提取：区分手动/自动字幕，列出语言和格式
- [ ] 3.5 定义 Pydantic 数据模型：VideoInfo、FormatInfo、SubtitleInfo、PlaylistInfo

## 4. 后端 API 端点

- [ ] 4.1 实现 POST /api/v1/video/info：接收 URL，返回视频元数据（标题、时长、缩略图、格式、字幕）
- [ ] 4.2 实现 POST /api/v1/playlist/info：接收播放列表/频道 URL，返回视频列表（支持分页）
- [ ] 4.3 实现 POST /api/v1/download：触发下载任务，接收 URL + 格式选择参数
- [ ] 4.4 实现 GET /api/v1/download/queue：返回当前下载队列状态
- [ ] 4.5 实现 POST /api/v1/download/{id}/pause：暂停下载任务
- [ ] 4.6 实现 POST /api/v1/download/{id}/resume：恢复下载任务
- [ ] 4.7 实现 POST /api/v1/download/{id}/cancel：取消下载任务
- [ ] 4.8 实现 GET/PUT /api/v1/settings：获取和更新应用设置

## 5. 下载管理器

- [ ] 5.1 实现下载队列管理器（download_mgr.py）：任务添加、移除、状态管理
- [ ] 5.2 实现并发下载控制：可配置的最大并发数（默认 3）
- [ ] 5.3 实现 yt-dlp progress_hooks 回调：捕获下载进度
- [ ] 5.4 实现 WebSocket 进度推送（progress.py）：实时向前端推送下载进度
- [ ] 5.5 实现暂停/恢复/取消下载：利用 yt-dlp 的中断机制
- [ ] 5.6 实现下载完成通知：通过 WebSocket 推送完成事件

## 6. 前端页面与组件

- [ ] 6.1 实现应用主布局：侧边导航栏 + 内容区域（HomeView、DownloadView、SettingsView）
- [ ] 6.2 实现 URL 输入组件：输入框 + 解析按钮，支持回车触发
- [ ] 6.3 实现视频信息展示组件：标题、时长、上传者、缩略图卡片
- [ ] 6.4 实现格式选择组件：格式列表表格，支持排序、筛选，选中后下载
- [ ] 6.5 实现字幕选择组件：字幕语言列表，勾选下载，格式选择
- [ ] 6.6 实现播放列表浏览组件：视频列表 + 全选/单选复选框 + 批量下载按钮
- [ ] 6.7 实现下载队列页面：任务列表、进度条、速度显示、暂停/恢复/取消按钮
- [ ] 6.8 实现设置页面：下载目录选择、默认画质、代理配置、并发数、语言切换

## 7. 前端状态管理与 API 对接

- [ ] 7.1 实现 Pinia store：videoStore（视频信息缓存）
- [ ] 7.2 实现 Pinia store：downloadStore（下载队列状态、WebSocket 进度监听）
- [ ] 7.3 实现 Pinia store：settingsStore（设置读写、持久化到后端）
- [ ] 7.4 实现 API 封装层（api/）：axios 实例、请求拦截、错误处理
- [ ] 7.5 实现 WebSocket 连接管理：自动连接、断线重连、消息分发

## 8. 打包与 CI/CD

- [ ] 8.1 编写 PyInstaller 打包脚本：将 Python 后端打包为单个可执行文件
- [ ] 8.2 配置 electron-builder：将 Python 可执行文件作为 extraResources 嵌入
- [ ] 8.3 编写 GitHub Actions workflow：build-windows.yml（Windows 构建）
- [ ] 8.4 编写 GitHub Actions workflow：build-macos.yml（macOS 构建）
- [ ] 8.5 编写 GitHub Actions workflow：release.yml（tag 触发自动发布到 GitHub Release）

## 9. 测试与验证

- [ ] 9.1 后端单元测试：yt-dlp 封装层、URL 类型识别、格式解析
- [ ] 9.2 后端 API 测试：各端点的正常/异常场景
- [ ] 9.3 前端组件测试：关键组件的渲染和交互
- [ ] 9.4 端到端验证：完整流程（输入 URL → 解析 → 选择格式 → 下载 → 完成通知）
- [ ] 9.5 打包验证：在 Windows 和 macOS 上验证打包产物可正常运行
