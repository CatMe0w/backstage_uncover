# backstage_uncover

_Uncover the backstages._

中文版请见[这里](https://github.com/CatMe0w/backstage_uncover/blob/master/README_zh.md)。

A tool to extract all logs from admin panels ("[backstages](https://github.com/52fisher/TiebaPublicBackstage)") of Baidu Tieba.

## Install dependencies

Python 3 is required.

`pip3 install lxml requests`

## Usage

`python3 main.py <tieba_name> <bduss>`

After logging in any baidu.com products in a browser, `BDUSS` can be extracted from cookies under `baidu.com`.

__Protect `BDUSS` like a password!__

## Notes
### Project Ex Nihilo data

All tags, releases, and GitHub Actions workflows in this repository are a part of Project Ex Nihilo, a project that archives all data of a specific forum.

Therefore, these data are not a part of this project. They are kept in order to provide an unbiased source of the data.

If you wish to use, clone or fork this repository, please ignore or remove these data.

## File strcutures

`uncover-raw/`: Raw HTML files of every page

`uncover.db`: SQLite database of parsed data

`uncover.log`: Log file

## Database structures

`posts`: Logs about posts and threads being deleted or restored

|Key|Type|Note|
|-|-|-|
|thread_id|numeric||
|post_id|numeric|Unique numeric id of every reply|
|title|text||
|content_preview|text|Content preview of the initial post of a thread|
|media|text|Link(s) of embedded pictures and videos|
|username|text||
|post_time|text|UTC+8, yyyy-MM-dd HH:mm|
|operation|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

`users`: Logs about users being banned or unbanned

|Key|Type|Note|
|-|-|-|
|avatar|text|Link of a user's avatar picture|
|username|text||
|operation|text||
|duration|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

`bawu`: lit. "staff". Logs about changes of staff

|Key|Type|Note|
|-|-|-|
|avatar|text|Link of a user's avatar picture|
|username|text||
|operation|text||
|operator|text||
|operation_time|text|UTC+8, yyyy-MM-dd HH:mm|

## License

[MIT License](https://opensource.org/licenses/MIT)
