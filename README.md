# backstage_uncover
A tool to extract all logs from admin panels ("[backstages](https://github.com/52fisher/TiebaPublicBackstage)") of Baidu Tieba.

## File strcutures
`uncover-raw/`: Raw HTML files of every page

`uncover.db`: SQLite database of parsed data

## Database structures
Tables: 

`posts`: Logs about posts and threads being deleted or restored

`users`: Logs about users being banned or unbanned

`bawu`: lit. "staff". Logs about changes of staff

## License
[MIT License](https://opensource.org/licenses/MIT)
