## ADDED Requirements

### Requirement: 下载目录设置

系统 SHALL 允许用户设置默认下载目录，并在设置中显示当前路径。

#### Scenario: 修改下载目录
- **WHEN** 用户在设置中点击"选择目录"并选择一个文件夹
- **THEN** 系统将下载目录更新为新路径，后续下载保存到该目录

#### Scenario: 下载目录不存在时自动创建
- **WHEN** 用户设置的下载目录不存在
- **THEN** 系统在首次下载时自动创建该目录

### Requirement: 默认画质设置

系统 SHALL 允许用户设置默认的下载画质偏好。

#### Scenario: 设置默认画质
- **WHEN** 用户在设置中选择默认画质（如"最高画质"、"1080p"、"720p"、"仅音频"）
- **THEN** 后续新下载任务默认使用该画质，无需每次手动选择

### Requirement: 代理配置

系统 SHALL 允许用户配置网络代理，用于访问 YouTube。

#### Scenario: 设置 HTTP 代理
- **WHEN** 用户在设置中输入代理地址（如 `http://127.0.0.1:7890`）
- **THEN** 系统通过该代理发起所有 YouTube 请求

#### Scenario: 设置 SOCKS5 代理
- **WHEN** 用户在设置中输入 SOCKS5 代理地址
- **THEN** 系统通过该 SOCKS5 代理发起请求

#### Scenario: 清除代理
- **WHEN** 用户清除代理设置
- **THEN** 系统恢复直连模式

### Requirement: 并发下载数设置

系统 SHALL 允许用户设置最大并发下载数。

#### Scenario: 修改并发数
- **WHEN** 用户在设置中调整最大并发下载数（1-10）
- **THEN** 系统按新的并发数限制下载队列

### Requirement: 语言设置

系统 SHALL 支持界面语言切换（中文/英文）。

#### Scenario: 切换界面语言
- **WHEN** 用户在设置中切换语言为中文或英文
- **THEN** 界面文字切换为对应语言，设置立即生效

### Requirement: 设置持久化

系统 SHALL 将用户设置持久化存储，应用重启后恢复。

#### Scenario: 设置保存
- **WHEN** 用户修改任何设置项
- **THEN** 设置自动保存到本地配置文件

#### Scenario: 设置恢复
- **WHEN** 应用启动时
- **THEN** 系统从配置文件加载上次的设置
