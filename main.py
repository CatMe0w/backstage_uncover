import re
import time
import datetime
import requests
from random import randint
from lxml import etree

TIEBA_NAME = ''
BDUSS = ''
MAX_PAGE = 1

backstage_log = []

cached_nicknames = {}


def get_post_id(url_params, thread_id):
    pseudo_post_id = re.findall('(?<=#).*', url_params)[0]
    if pseudo_post_id == thread_id:
        return None
    else:
        return pseudo_post_id


def get_nickname(username, nickname_raw):
    if username == nickname_raw:
        return username
    if cached_nicknames.__contains__(username):
        return cached_nicknames[username]

    if nickname_raw == '--': # 已注销用户
        return None
    if nickname_raw[:4] == '百度用户': # 已屏蔽用户，通常是爆吧机器人
        return None
    try:
        time.sleep(randint(1500, 2500) / 1000)
        nickname_response = requests.get(
            'https://tieba.baidu.com/home/main?un=' + username, headers=headers)
    except:
        return None
    # 若为None，代表该用户已被百度屏蔽，或是使用IP发帖的匿名用户
    # 离谱的来了，2019年之后哪来的匿名用户？我到底要为这个垃圾产品补充多少的edge case处理？

    nickname_tree = etree.HTML(nickname_response.content)
    nickname = nickname_tree.xpath('/html/head/title/text()')[0][:-3]
    if nickname == '百度安': # “百度安全验证”风控
        raise NotImplementedError
    cached_nicknames.update({username: nickname})
    return nickname


def get_post_time(post_time_raw, thread_id):
    # post_time_raw 形如 'MM月dd日 HH:mm'
    month = int(post_time_raw[:2])
    day = int(post_time_raw[3:5])
    hour = int(post_time_raw[7:9])
    minute = int(post_time_raw[10:12])
    p = int(thread_id)
    if p < 966676089:
        raise NotImplementedError
    elif p < 1347023954:
        year = 2011
    elif p < 2076654372:
        year = 2012
    elif p < 2790164985:
        year = 2013
    elif p < 3499710968:
        year = 2014
    elif p < 4243777598:
        year = 2015
    elif p < 4922225497:
        year = 2016
    elif p < 5499472409:
        year = 2017
    elif p < 5994564429:
        year = 2018
    elif p < 6421708311:
        year = 2019
    elif p < 7175996965:
        year = 2020
    else:
        year = 2021
    # Oh, FUCK BAIDU!
    # 这些数字是整个百度贴吧产品每年第一个帖子的id
    # 百度没有为后台日志显示的发帖时间提供年份，因此不得不通过硬编码这些数字的方式来推算出正确的年份。
    return datetime.datetime(year, month, day, hour, minute)


def get_operation_time(operation_date_raw, operation_time_raw):
    return datetime.datetime.strptime(operation_date_raw + ' ' + operation_time_raw, '%Y-%m-%d %H:%M')


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

    content = response.content.decode('gbk')
    tree = etree.HTML(content)
    for j in range(1, 31):
        try:
            url_params = tree.xpath(
                '//*[@id="container"]/div[2]/div[2]/table/tbody/tr[{}]/td[1]/article/div[2]/h1/a/@href'.format(j))[0][3:]
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
    
        thread_id = re.findall('.+?(?=\?)', url_params)[0]
        post_id = get_post_id(url_params, thread_id)
        nickname = get_nickname(username, nickname_raw)
        # 从后台直接获取的昵称中，若该昵称含有emoji，该emoji将显示为一张图片，且存放在另外的标签中。
        # 为了解决这个问题，需要访问该用户的用户页，从网页标题获取正常的emoji字符。
        post_time = get_post_time(post_time_raw, thread_id)
        operation_time = get_operation_time(
            operation_date_raw, operation_time_raw)

        log_entry = [thread_id, post_id, title, content_preview, media_list, username, nickname,
                     post_time, operation, operator, operation_time]
        backstage_log.append(log_entry)
