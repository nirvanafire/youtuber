## Why

需要一个自用的 YouTube 视频下载桌面工具，能够解析视频信息、选择清晰度和字幕、浏览播放列表/频道集合，并管理下载队列。现有命令行工具（yt-dlp）功能强大但缺乏图形化界面，操作效率低。通过构建 Electron + Vue3 桌面应用，封装 yt-dlp 的能力为可视化的现代 UI，提升日常使用体验。

## What Changes

- 新建完整的 Electron + Vue3 + TypeScript 前端项目，使用 Element Plus 组件库
- 新建 Python FastAPI 后端，以库模式调用 yt-dlp，提供 REST API + WebSocket 接口
- 实现 URL 解析：自动识别单视频、播放列表、频道等链接类型
- 实现视频信息展示：标题、时长、缩略图、可用格式/清晰度列表
- 实现字幕发现与下载：展示可用语言，支持下载和内嵌
- 实现播放列表/集合浏览：列出所有视频，支持批量选择下载
- 实现下载队列管理：并发下载、实时进度、暂停/恢复/取消
- 实现设置面板：下载目录、默认画质、代理配置、语言设置
- Python 环境管理：优先使用用户本地 Python 3.10+，回退到内嵌便携版
- GitHub Actions CI/CD：自动构建 Windows (.exe/.msi) 和 macOS (.dmg) 安装包

## Capabilities

### New Capabilities
- `video-info-extraction`: 解析 YouTube URL，提取视频元数据（标题、时长、缩略图、可用格式、字幕）
- `format-selection`: 展示所有可用视频/音频格式，支持按清晰度、编码、大小筛选和选择
- `subtitle-management`: 发现可用字幕（手动/自动生成），支持多语言下载和格式选择
- `playlist-browsing`: 识别播放列表/频道链接，列出所有视频，支持分页和批量选择
- `download-management`: 下载队列管理，支持并发、实时进度推送、暂停/恢复/取消
- `settings-management`: 应用配置管理，包括下载目录、默认质量、代理、语言等
- `python-environment`: Python 运行时检测与管理，支持本地环境和内嵌便携版
- `electron-python-bridge`: Electron 主进程与 Python 后端的通信桥接（进程管理、健康检查、API 代理）

### Modified Capabilities

（无，这是全新项目）

## Impact

- **新增依赖**: Electron, Vue3, Element Plus, Vite, TypeScript, Pinia, axios (前端); FastAPI, yt-dlp, PyInstaller, aiofiles, websockets (后端)
- **项目结构**: 新建 `electron/` 和 `backend/` 两个子项目
- **CI/CD**: 新增 `.github/workflows/` 配置，跨平台构建矩阵
- **运行环境**: 需要 Node.js (构建时) + Python 3.10+ (运行时)
- **打包产物**: Windows (.exe/.msi), macOS (.dmg), 总包体约 100-200MB
