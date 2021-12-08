import re
import requests
from lxml import etree

TIEBA_NAME = ''
BDUSS = ''
MAX_PAGE = 1

backstage_log = []

cached_nicknames = {}


def get_nickname(username):
    if cached_nicknames.__contains__(username):
        return cached_nicknames[username]
    while True:
        try:
            nickname_response = requests.get(
                'https://tieba.baidu.com/home/main?un=' + username)
        except:
            continue
        else:
            break
    nickname_tree = etree.HTML(nickname_response.content)
    nickname = nickname_tree.xpath('/html/head/title/text()')[0][:-3]
    cached_nicknames.update({username, nickname})
    return nickname


cookies = {
    'BDUSS': BDUSS,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
}

for i in range(1, MAX_PAGE + 1):
    params = (
        ('stype', ''),
        ('svalue', ''),
        ('begin', ''),
        ('end', ''),
        ('op_type', ''),
        ('word', TIEBA_NAME),
        ('pn', str(i)),
    )
    while True:
        try:
            response = requests.get('http://tieba.baidu.com/bawu2/platform/listPostLog',
                                    headers=headers, params=params, cookies=cookies, verify=False)
        except:
            continue
        else:
            break

    tree = etree.HTML(response.content)
    for j in range(1, 31):
        post_id = re.findall('.+?(?=\?)', tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/h1/a/@href'.format(j))[0][3:])[0]
        title = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/h1/a/@title'.format(j))[0]
        content_preview = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/div[1]/text()'.format(j))[0]
        username = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/div[1]/a/text()'.format(j))[0][4:]
        # nickname = tree.xpath(
        #     '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/div[2]/a/text()'.format(j))[0]
        nickname = get_nickname(username)
        # 从后台直接获取的昵称中，若该昵称含有emoji，该emoji将显示为一张图片，且存放在额外的标签中。
        # 为了解决这个问题，需要访问该用户的用户页，从网页标题获取正常的emoji字符。
        post_time = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/time/text()'.format(j))[0]
        operation = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[2]/span/text()'.format(j))[0]
        operator = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[3]/a/text()'.format(j))[0]
        operation_date = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[4]/text()[1]'.format(j))[0]
        operation_time = tree.xpath(
            '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[4]/text()[2]'.format(j))[0]

        log_entry = {post_id, title, content_preview, username, nickname,
                     post_time, operation, operator, operation_date, operation_time}
        backstage_log.append(log_entry)
