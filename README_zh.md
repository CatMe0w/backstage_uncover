# backstage_uncover

_揭开帷幕。_

一个用于提取百度贴吧吧务后台完整操作记录的工具。

## 安装依赖

需要 Python 3。

`pip3 install lxml requests`

## 使用方法

`python3 main.py <贴吧名> <bduss>`

在浏览器中登录任意百度产品，可在`baidu.com`下的 cookie 中找到 `BDUSS`。

__请像保护密码一样保护 `BDUSS`！__

## 注意
### Project Ex Nihilo 数据

本仓库内的所有 tag，release，以及 GitHub Actions workflow 均属于 Project Ex Nihilo，一个针对特定贴吧进行全量存档的工程。

因此，这些数据不是本项目的一部分。保留这些数据是为了提供一个公正的数据源。

如需使用、clone 或 fork 本仓库，请忽略或移除这些数据。

## 文件结构

`uncover-raw/`：每个页面的原始 HTML

`uncover.db`：存有已解析数据的 SQLite 数据库

`uncover.log`: 日志文件

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
