# backstage_uncover
一个用于提取百度贴吧吧务后台完整操作记录的工具。

## 文件结构
`uncover-raw/`：每个页面的原始 HTML

`uncover.db`：存有已解析数据的 SQLite 数据库

## 数据库结构
`posts`：帖子或回复被删除或恢复删除等操作的记录

|Key|Type|Note|
|-|-|-|
|thread_id|numeric||
|post_id|numeric|每一层楼的唯一 ID|
|title|text||
|content_preview|text|帖子的正文内容预览|
|media|text|图片或视频链接|
|username|text||
|post_time|text|UTC+8, yyyy-MM-dd HH:mm|
|operation|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

`users`：用户被封禁或解封等操作的记录
|Key|Type|Note|
|-|-|-|
|avatar|text|用户头像的图片链接|
|username|text||
|operation|text||
|duration|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

`bawu`：吧务人事变动记录
|Key|Type|Note|
|-|-|-|
|avatar|text|用户头像的图片链接|
|username|text||
|operation|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

## 开源许可
[MIT License](https://opensource.org/licenses/MIT)
