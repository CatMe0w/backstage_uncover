import time
import requests
from lxml import etree
from pathlib import Path
import sqlite3

TIEBA_NAME = ''
BDUSS = ''
MAX_PAGE_POSTS = 1
MAX_PAGE_USERS = 1
MAX_PAGE_BAWU = 1  # 百度的HTML中，原文如此。指“吧务”（人事变动）日志。


def get_post_id(url_params, thread_id, title):
    if title[:3] != '回复：':
        return None
    pseudo_post_id = url_params.split('#')[-1]
    if pseudo_post_id == thread_id:
        return None
    else:
        return pseudo_post_id


def get_media(media_list):
    if not media_list:
        return None
    return '\n'.join(media_list)


def get_post_time(post_time_raw, thread_id, post_id):
    # post_time_raw 形如 'MM月dd日 HH:mm'
    month = post_time_raw[:2]
    day = post_time_raw[3:5]
    hour = post_time_raw[7:9]
    minute = post_time_raw[10:12]
    t = int(thread_id)
    if t < 966676089:
        raise NotImplementedError
    elif t < 1347023954:
        year = 2011
    elif t < 2076654372:
        year = 2012
    elif t < 2790164985:
        year = 2013
    elif t < 3499710968:
        year = 2014
    elif t < 4243777606:
        year = 2015
    elif t < 4922225497:
        year = 2016
    elif t < 5499472409:
        year = 2017
    elif t < 5994564429:
        year = 2018
    elif t < 6421708311:
        year = 2019
    elif t < 7175996965:
        year = 2020
    else:
        year = 2021

    if post_id is not None:
        p = int(post_id)
        if p < 10820694325:
            raise NotImplementedError
        elif p < 16286454017:
            year = 2011
        elif p < 27783085247:
            year = 2012
        elif p < 43785897735:
            year = 2013
        elif p < 62390144947:
            year = 2014
        elif p < 81567711037:
            year = 2015
        elif p < 102026421151:
            year = 2016
        elif p < 116661024725:
            year = 2017
        elif p < 123468282107:
            year = 2018
        elif p < 129138716997:
            year = 2019
        elif p < 137282019373:
            year = 2020
        else:
            year = 2021
    # Oh, FUCK BAIDU!
    # 这些数字是整个百度贴吧产品每年第一个帖子的id
    # 百度没有为后台日志显示的发帖时间提供年份，因此不得不通过硬编码这些数字的方式来推算出正确的年份。
    return '{}-{}-{} {}:{}'.format(year, month, day, hour, minute)


print("""
Starting backstage_uncover

Target: {}
Pages of posts: {}
Pages of users: {}
Pages of bawu: {}

Weigh anchor!
""".format(TIEBA_NAME, MAX_PAGE_POSTS, MAX_PAGE_USERS, MAX_PAGE_BAWU))

Path("./uncover-raw/posts").mkdir(parents=True, exist_ok=True)
Path("./uncover-raw/users").mkdir(parents=True, exist_ok=True)
Path("./uncover-raw/bawu").mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect('uncover.db')
db = conn.cursor()
db.execute('''
    create table post(
    thread_id numeric not null,
    post_id numeric,
    title text not null,
    content_preview text not null,
    media text,
    username text not null,
    post_time text not null,
    operation text not null,
    operator text not null,
    operation_time text not null);''')
db.execute('''
    create table user(
    avatar text not null,
    username text not null,
    operation text not null,
    duration text,
    operator text not null,
    operation_time text not null);''')
db.execute('''
    create table bawu(
    avatar text not null,
    username text not null,
    operation text not null,
    operator text not null,
    operation_time text not null);''')
conn.commit()

cookies = {
    'BDUSS': BDUSS,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
}

for i in range(1, MAX_PAGE_POSTS + 1):
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
            print("Current page: posts, " + str(i))
            response = requests.get('http://tieba.baidu.com/bawu2/platform/listPostLog',
                                    headers=headers, params=params, cookies=cookies, verify=False)
        except requests.exceptions.Timeout:
            print("Remote is not responding, sleep for 30s.")
            time.sleep(30)
            continue
        else:
            break
    with open('./uncover-raw/posts/{}.html'.format(i), 'wb') as f:
        f.write(response.content)

    content = response.content.decode('gbk')
    tree = etree.HTML(content)
    for j in range(1, 31):
        try:
            url_params = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/h1/a/@href'.format(j))[0]
            title = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/h1/a/@title'.format(j))[0]
            content_preview = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/div[1]/text()'.format(j))[0][12:]
            media_list = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/div[2]/ul[1]/li/a/@href'.format(j))
            username = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/div[1]/a/text()'.format(j))[0][5:]
            nickname_raw = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/div[2]/a/text()'.format(j))[0][4:]
            post_time_raw = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[1]/time/text()'.format(j))[0]
            operation = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[2]/span/text()'.format(j))[0]
            operator = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[3]/a/text()'.format(j))[0]
            operation_date_raw = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[4]/text()[1]'.format(j))[0]
            operation_time_raw = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[4]/text()[2]'.format(j))[0]
        except IndexError:
            continue
        # 正常情况下，一页日志共有30项记录，但个别页可能出现少于30项的情况

        thread_id = url_params.split('/')[-1].split('?')[0]
        post_id = get_post_id(url_params, thread_id, title)
        media = get_media(media_list)
        post_time = get_post_time(post_time_raw, thread_id, post_id)
        operation_time = operation_date_raw + ' ' + operation_time_raw

        db.execute('insert into post values(?,?,?,?,?,?,?,?,?,?)',
                   (thread_id, post_id, title, content_preview, media, username, post_time, operation, operator, operation_time))
    conn.commit()

for i in range(1, MAX_PAGE_USERS + 1):
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
            print("Current page: users, " + str(i))
            response = requests.get('http://tieba.baidu.com/bawu2/platform/listUserLog',
                                    headers=headers, params=params, cookies=cookies, verify=False)
        except requests.exceptions.Timeout:
            print("Remote is not responding, sleep for 30s.")
            time.sleep(30)
            continue
        else:
            break
    with open('./uncover-raw/users/{}.html'.format(i), 'wb') as f:
        f.write(response.content)

    content = response.content.decode('gbk')
    tree = etree.HTML(content)
    for j in range(1, 31):
        try:
            avatar = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[1]/a/img/@src'.format(j))[0]
            username = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[1]/a/text()'.format(j))[0][36:]
            operation = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[3]/text()'.format(j))[0]
            duration = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[4]/text()'.format(j))[0][60:-28]  # 这么阴间的HTML到底是怎么产生的？
            operator = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[5]/a/text()'.format(j))[0]
            operation_time = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[6]/text()'.format(j))[0]
        except IndexError:
            continue
        # 同上

        if duration == '--' or duration == '':
            duration = None

        db.execute('insert into user values(?,?,?,?,?,?)',
                   (avatar, username, operation, duration, operator, operation_time))
    conn.commit()

for i in range(1, MAX_PAGE_BAWU + 1):
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
            print("Current page: bawu, " + str(i))
            response = requests.get('http://tieba.baidu.com/bawu2/platform/listBawuLog',
                                    headers=headers, params=params, cookies=cookies, verify=False)
        except requests.exceptions.Timeout:
            print("Remote is not responding, sleep for 30s.")
            time.sleep(30)
            continue
        else:
            break
    with open('./uncover-raw/bawu/{}.html'.format(i), 'wb') as f:
        f.write(response.content)

    content = response.content.decode('gbk')
    tree = etree.HTML(content)
    for j in range(1, 31):
        try:
            avatar = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[1]/a/img/@src'.format(j))[0]
            username = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[1]/a/text()'.format(j))[0][32:]
            operation = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[2]/text()'.format(j))[0]
            operator = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[3]/a/text()'.format(j))[0]
            operation_time = tree.xpath(
                '//*[@id="dataTable"]/tbody/tr[{}]/td[4]/text()'.format(j))[0]
        except IndexError:
            continue
        # 同上

        db.execute('insert into bawu values(?,?,?,?,?)',
                   (avatar, username, operation, operator, operation_time))
    conn.commit()

conn.close()
