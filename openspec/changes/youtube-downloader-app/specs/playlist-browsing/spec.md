## ADDED Requirements

### Requirement: 识别并加载播放列表

系统 SHALL 识别 YouTube 播放列表 URL，加载并展示播放列表中的所有视频。

#### Scenario: 解析播放列表 URL
- **WHEN** 用户输入 `https://www.youtube.com/playlist?list=xxx` 格式的 URL
- **THEN** 系统返回播放列表元数据（标题、创建者、视频总数）和视频列表

#### Scenario: 播放列表视频列表展示
- **WHEN** 播放列表加载完成
- **THEN** 系统以列表形式展示每个视频的标题、时长、缩略图

#### Scenario: 大型播放列表分页加载
- **WHEN** 播放列表包含超过 50 个视频
- **THEN** 系统使用分页或懒加载方式展示，避免一次性加载全部

### Requirement: 识别并加载频道视频列表

系统 SHALL 识别 YouTube 频道 URL，加载并展示该频道的视频列表。

#### Scenario: 解析频道 URL
- **WHEN** 用户输入 `https://www.youtube.com/@channel` 或 `https://www.youtube.com/channel/xxx` 格式的 URL
- **THEN** 系统返回频道信息和最近的视频列表

#### Scenario: 频道视频分页浏览
- **WHEN** 频道有大量视频
- **THEN** 系统支持分页加载更多视频

### Requirement: 批量选择视频

系统 SHALL 允许用户从播放列表或频道视频列表中选择多个视频进行批量操作。

#### Scenario: 全选/取消全选
- **WHEN** 用户点击"全选"按钮
- **THEN** 列表中所有视频被选中；再次点击取消全选

#### Scenario: 单独选择/取消选择
- **WHEN** 用户点击某个视频的复选框
- **THEN** 该视频的选中状态切换

#### Scenario: 对选中视频执行批量下载
- **WHEN** 用户选中多个视频后点击"下载选中"
- **THEN** 所有选中视频加入下载队列，使用当前选择的格式设置
