# -*- coding: utf-8 -*-
"""
Project: WechatMpBot
Creator: DoubleThunder
Create time: 2019-12-02 16:42
Introduction: 小说追更，基于《笔趣阁》爬虫。

需要安装的库
requests
BeautifulSoup
fake_useragent
yagmail
apscheduler
"""

import re
import json
import dbm

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import yagmail
from apscheduler.schedulers.blocking import BlockingScheduler

search_url = 'https://www.5atxt.com/index.php?s=/web/index/search'
base_url = 'https://www.5atxt.com'


def get_home_url(novel_name: str) -> str:
    """
    获取小说的主页面 url
    :param novel_name: 小说名
    :return:
    """
    data = {'name': novel_name}
    headers = {'User-Agent': fake_ua.random}
    try:
        resp = requests.post(search_url, headers=headers, data=data)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            nhs = soup.find_all('span', class_='s2', text=novel_name)
            if nhs:
                nh = nhs[-1]
                href = nh.a.get('href')
                home_url = "{}{}".format(base_url, href)
                return home_url

    except Exception as exception:
        print(str(exception))
    return None


def get_new_chapter(novel_name: str) -> str:
    home_url = novel_home_dict.get(novel_name)
    if not home_url:
        home_url = get_home_url(novel_name)
        if not home_url:
            print('没有在此网站找到《{}》'.format(novel_name))
            return
        # 保存小说详情页
        novel_home_dict[novel_name] = home_url

    # 取出最后一次更新保存的章节名
    old_chapter_name = novel_chapter_dict.get(novel_name)
    headers = {'User-Agent': fake_ua.random}

    try:
        resp = requests.get(home_url, headers=headers)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.text, "lxml")

        latest_chapter_a = soup.select("div#info > p:nth-last-child(1)")[0].a
        # latest_chapter_a = soup.find(lambda tag: tag.name == 'p' and '最新章节：' in tag.text).a

        latest_chapter_name = latest_chapter_a.text.strip()  # 最新章节名称
        latest_chapter_url = latest_chapter_a['href']  # 最新章节地址
        latest_chapter_url = "{}{}".format(base_url, latest_chapter_url)

        if not old_chapter_name:  # 如果章节名不存在，则说明这是第一次访问，直接更新
            content = get_novel_content(latest_chapter_url)
            if content:
                send_mail(novel_name, latest_chapter_name, content)
                novel_chapter_dict[novel_name] = latest_chapter_name
            return

        if latest_chapter_name == old_chapter_name:
            print('小说还没有更新')
            return

        # 找到上一次保存的章节名所在位置
        old_chap = soup.find_all('a', text=re.compile(old_chapter_name))
        if not old_chap:  # 上一次保存的章节名，有问题。直接更新最新一章
            content = get_novel_content(latest_chapter_url)
            if content:
                send_mail(novel_name, latest_chapter_name, content)
                novel_chapter_dict[novel_name] = latest_chapter_name
            return

        # 有可能更新多章
        # 检索上一次的章节——最新的章节，这就是已更新的章节了
        new_chap = old_chap[-1].parent.find_next_siblings('dd')
        if new_chap:
            for item in new_chap:
                chapter = item.text.strip()
                href = item.a.get('href')
                url = "{}{}".format(base_url, href)
                content = get_novel_content(url)
                if content:
                    send_mail(novel_name, chapter, content)

            # 保存最新一章的章节名
            novel_chapter_dict[novel_name] = latest_chapter_name
            return
        else:
            print('小说还没有更新')

    except Exception as exception:
        print(str(exception))


def get_novel_content(url: str) -> str:
    """
    从小说页获取小说内容。
    :param url: 小说url
    :return: 小说内容
    """
    try:
        headers = {'User-Agent': fake_ua.random}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            aa = soup.find('div', id='content', deep="3")
            if aa.p:
                # 用于删除：天才一秒记住本站地址：[笔趣阁] https://www.5atxt.com最快更新！无广告！
                aa.p.decompose()
            if aa.div:
                # 用于删除：章节错误,点此报送(免注册), 报送后维护人员会在两分钟内校正章节内容,请耐心等待。
                aa.div.decompose()
            return str(aa)
        return None
    except Exception as exception:
        print(str(exception))
        return None
    return None


def send_mail(novel_name: str, chapter: str, content: str) -> None:
    """
    把小说发送邮件
    :param novel_name: 小说名
    :param chapter: 章节名
    :param content: 小说内容
    :return:
    """
    try:
        if not content:
            return
        title = '{} {}'.format(novel_name, chapter)
        yag.send(to_emails, title, content)
        print('已发送邮件:{}'.format(title))
    except Exception as exception:
        print(str(exception))


def update_novel() -> None:
    """ 检查更新 """
    for novel_name in novel_name_list:
        get_new_chapter(novel_name)


if __name__ == '__main__':
    print('启动成功')

    # 需要追更的小说
    novel_name_list = ['诡秘之主']

    email_user = 'form@qq.com'
    email_password = '密码'
    email_host = 'smtp.qq.com'
    to_emails = ['to@qq.com']  # 需要发送的邮箱，可以多个。

    try:
        yag = yagmail.SMTP(user=email_user, password=email_password, host=email_host)
        yag.login()
    except Exception as exception:
        print('邮件信息填写有误，已退出！')
        exit(-1)

    fake_ua = UserAgent()
    novel_home_dict = {}  # 保存小说详情页地址
    novel_chapter_dict = {}  # 保存小说最新章节名

    update_novel()  # 立马更新一次。

    scheduler = BlockingScheduler()
    scheduler.add_job(update_novel, 'interval', minutes=30, misfire_grace_time=600, jitter=300)
    scheduler.start()
