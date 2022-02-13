import sys
import time
import sqlite3
import logging
import requests
from lxml import etree
from pathlib import Path


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
    elif t < 7679713980:
        year = 2021
    else:
        year = 2022

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
        elif p < 142697363810:
            year = 2021
        else:
            year = 2022
    # Oh, FUCK BAIDU!
    # 这些数字是整个百度贴吧产品每年第一个帖子的id
    # 百度没有为后台日志显示的发帖时间提供年份，因此不得不通过硬编码这些数字的方式来推算出正确的年份。
    return '{}-{}-{} {}:{}'.format(year, month, day, hour, minute)


def main(tieba_name, bduss):
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler("uncover.log"),
            logging.StreamHandler()
        ])

    logging.info("""
    Starting backstage_uncover
    
    Target: {}
    
    Weigh anchor!
    """.format(tieba_name))

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
        'BDUSS': bduss,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    }

    session = requests.Session()

    max_page = 1
    page = 1
    while True:
        params = (
            ('stype', ''),
            ('svalue', ''),
            ('begin', ''),
            ('end', ''),
            ('op_type', ''),
            ('word', tieba_name),
            ('pn', str(page)),
        )

        while True:
            try:
                logging.info("Current page: posts, " + str(page))
                response = session.get('http://tieba.baidu.com/bawu2/platform/listPostLog',
                                       headers=headers, params=params, cookies=cookies)
            except requests.exceptions.Timeout:
                logging.warning("Remote is not responding, sleep for 30s.")
                time.sleep(30)
                continue
            else:
                break
        with open('./uncover-raw/posts/{}.html'.format(page), 'wb') as f:
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

        if page == 1:
            max_page = int(tree.xpath('//*[@id="container"]/div[2]/div[2]/div[2]/span/text()')[0].strip('共').strip('页'))
            logging.info('Pages of posts: {}'.format(max_page))
        if page == max_page:
            break
        else:
            page += 1

    page = 1
    while True:
        params = (
            ('stype', ''),
            ('svalue', ''),
            ('begin', ''),
            ('end', ''),
            ('op_type', ''),
            ('word', tieba_name),
            ('pn', str(page)),
        )

        while True:
            try:
                logging.info("Current page: users, " + str(page))
                response = session.get('http://tieba.baidu.com/bawu2/platform/listUserLog',
                                       headers=headers, params=params, cookies=cookies)
            except requests.exceptions.Timeout:
                logging.warning("Remote is not responding, sleep for 30s.")
                time.sleep(30)
                continue
            else:
                break
        with open('./uncover-raw/users/{}.html'.format(page), 'wb') as f:
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

        if page == 1:
            max_page = int(tree.xpath('//*[@id="container"]/div[2]/div[2]/div[2]/span/text()')[0].strip('共').strip('页'))
            logging.info('Pages of users: {}'.format(max_page))
        if page == max_page:
            break
        else:
            page += 1

    page = 1
    while True:
        params = (
            ('stype', ''),
            ('svalue', ''),
            ('begin', ''),
            ('end', ''),
            ('op_type', ''),
            ('word', tieba_name),
            ('pn', str(page)),
        )

        while True:
            try:
                logging.info("Current page: bawu, " + str(page))
                response = session.get('http://tieba.baidu.com/bawu2/platform/listBawuLog',
                                       headers=headers, params=params, cookies=cookies)
            except requests.exceptions.Timeout:
                logging.warning("Remote is not responding, sleep for 30s.")
                time.sleep(30)
                continue
            else:
                break
        with open('./uncover-raw/bawu/{}.html'.format(page), 'wb') as f:
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

        if page == 1:
            max_page = int(tree.xpath('//*[@id="container"]/div[2]/div[2]/div[2]/span/text()')[0].strip('共').strip('页'))
            logging.info('Pages of bawu: {}'.format(max_page))
        if page == max_page:
            break
        else:
            page += 1

    conn.close()
    logging.info('All done! Have fun!')


if __name__ == '__main__':
    if not sys.argv[2:]:
        print('Usage: python3 {} <tieba_name> <bduss>'.format(sys.argv[0]))
        exit(1)
    main(str(sys.argv[1]), str(sys.argv[2]))
