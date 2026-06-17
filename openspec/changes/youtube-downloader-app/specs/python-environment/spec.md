## ADDED Requirements

### Requirement: 检测用户本地 Python 环境

系统 SHALL 在启动时检测用户机器上是否有可用的 Python 3.10+ 环境。

#### Scenario: 检测到可用 Python
- **WHEN** 用户机器上安装了 Python 3.10 或更高版本
- **THEN** 系统记录 Python 路径，优先使用该环境启动后端

#### Scenario: 未检测到 Python 或版本过低
- **WHEN** 用户机器上没有 Python 或版本低于 3.10
- **THEN** 系统回退到使用内嵌的便携版 Python

#### Scenario: 检测多个 Python 版本
- **WHEN** 用户机器上有多个 Python 版本
- **THEN** 系统选择满足要求的最新版本

### Requirement: 内嵌便携版 Python 作为后备

系统 SHALL 在 Electron 打包时内嵌一个 Python 便携版环境，作为用户没有 Python 时的后备方案。

#### Scenario: 使用内嵌 Python 启动后端
- **WHEN** 用户机器上无可用 Python 环境
- **THEN** 系统使用内嵌的便携版 Python 启动 FastAPI 后端

#### Scenario: 内嵌 Python 包含必要依赖
- **WHEN** 系统使用内嵌 Python 时
- **THEN** 便携版 Python 环境中已包含 yt-dlp、fastapi 等所有必要依赖

### Requirement: Python 环境状态展示

系统 SHALL 在设置页面展示当前使用的 Python 环境信息。

#### Scenario: 显示 Python 环境信息
- **WHEN** 用户查看设置页面的环境信息
- **THEN** 系统显示：Python 版本、路径（本地/内嵌）、yt-dlp 版本
