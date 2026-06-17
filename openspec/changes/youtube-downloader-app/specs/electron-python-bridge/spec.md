## ADDED Requirements

### Requirement: Python 后端进程生命周期管理

系统 SHALL 由 Electron 主进程管理 Python FastAPI 后端的启动、运行和关闭。

#### Scenario: 启动 Python 后端
- **WHEN** Electron 应用启动
- **THEN** 主进程启动 Python FastAPI 子进程，使用随机可用端口

#### Scenario: 健康检查
- **WHEN** Python 后端进程启动后
- **THEN** 主进程定期发送健康检查请求（GET /health），直到收到成功响应

#### Scenario: 后端崩溃自动重启
- **WHEN** Python 后端进程意外退出
- **THEN** 主进程检测到退出后自动重启后端（最多重试 3 次）

#### Scenario: 优雅关闭
- **WHEN** Electron 应用关闭
- **THEN** 主进程向 Python 后端发送终止信号，等待其优雅退出后关闭

### Requirement: API 代理转发

系统 SHALL 由 Electron 主进程将渲染进程的 API 请求代理转发到 Python 后端。

#### Scenario: REST API 代理
- **WHEN** 渲染进程发起 HTTP 请求到 `/api/v1/...`
- **THEN** 主进程将请求转发到 Python 后端的对应端口

#### Scenario: WebSocket 代理
- **WHEN** 渲染进程建立 WebSocket 连接到 `/ws`
- **THEN** 主进程将 WebSocket 连接代理到 Python 后端的 WebSocket 端点

### Requirement: 后端端口通信

系统 SHALL 通过 stdout 管道在 Electron 主进程和 Python 后端之间传递端口信息。

#### Scenario: Python 后端输出端口
- **WHEN** Python FastAPI 启动并监听端口
- **THEN** 后端向 stdout 输出端口号（格式: `PORT=xxxxx`）

#### Scenario: Electron 主进程读取端口
- **WHEN** 主进程从 Python 进程的 stdout 读取到端口号
- **THEN** 主进程使用该端口与后端通信

### Requirement: 前端 Loading 状态

系统 SHALL 在 Python 后端启动期间向用户展示加载状态。

#### Scenario: 后端启动中显示 Loading
- **WHEN** Python 后端正在启动（健康检查未通过）
- **THEN** 前端显示加载动画和"正在初始化..."提示

#### Scenario: 后端就绪后显示主界面
- **WHEN** 健康检查通过
- **THEN** 前端隐藏加载动画，显示应用主界面

#### Scenario: 启动超时提示
- **WHEN** 后端启动超过 30 秒仍未通过健康检查
- **THEN** 前端显示启动失败提示，提供重试和查看日志的选项
