## ADDED Requirements

### Requirement: 解析 YouTube URL 并提取视频元数据

系统 SHALL 接受用户输入的 YouTube URL，通过 yt-dlp 库提取视频的结构化元数据，包括标题、时长、上传者、缩略图 URL、可用格式列表和可用字幕列表。

#### Scenario: 解析单个视频链接
- **WHEN** 用户输入 `https://www.youtube.com/watch?v=xxx` 格式的 URL
- **THEN** 系统返回该视频的完整元数据（标题、时长、上传者、缩略图、可用格式列表、可用字幕列表）

#### Scenario: 解析短视频链接
- **WHEN** 用户输入 `https://www.youtube.com/shorts/xxx` 格式的 URL
- **THEN** 系统正确识别并返回该短视频的元数据

#### Scenario: 输入无效 URL
- **WHEN** 用户输入无法识别的 URL 格式
- **THEN** 系统返回明确的错误信息，说明 URL 无法解析

#### Scenario: 视频不可用（私有/已删除/地区限制）
- **WHEN** 用户输入的 URL 指向不可用的视频
- **THEN** 系统返回明确的错误信息，说明视频不可用的原因

### Requirement: URL 类型自动识别

系统 SHALL 自动识别输入 URL 的类型（单视频、播放列表、频道），并根据类型返回对应的数据结构。

#### Scenario: 识别单视频 URL
- **WHEN** 用户输入 `https://www.youtube.com/watch?v=xxx`
- **THEN** 系统识别为单视频类型，返回单个视频的元数据

#### Scenario: 识别包含播放列表的 URL
- **WHEN** 用户输入 `https://www.youtube.com/watch?v=xxx&list=xxx`
- **THEN** 系统识别为视频+播放列表类型，返回视频元数据和所属播放列表信息
