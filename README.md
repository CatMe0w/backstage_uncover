# backstage_uncover
A tool to extract all logs from admin panels ("[backstages](https://github.com/52fisher/TiebaPublicBackstage)") of Baidu Tieba.

## File strcutures
`uncover-raw/`: Raw HTML files of every page

`uncover.db`: SQLite database of parsed data

## Database structures
Tables: 

`posts`: Logs about posts and threads being deleted or restored

|Key|Type|Note|
|-|-|-|
|thread_id|numeric||
|post_id|numeric|Unique numeric id of every reply|
|title|text||
|content_preview|text|Content preview of the initial post of a thread|
|media|text|Link(s) of embedded pictures and videos|
|username|text||
|post_time|text|UTC+8|
|operation|text||
|operator|text||
|operation_time|text|UTC+8|

`users`: Logs about users being banned or unbanned
|Key|Type|Note|
|-|-|-|
|avatar|text|Link of a user's avatar picture|
|username|text||
|operation|text||
|duration|text||
|operator|text||
|operation_time|text|UTC+8|

`bawu`: lit. "staff". Logs about changes of staff
|Key|Type|Note|
|-|-|-|
|avatar|text|Link of a user's avatar picture|
|username|text||
|operation|text||
|operator|text||
|operation_time|text|UTC+8|

## License
[MIT License](https://opensource.org/licenses/MIT)
