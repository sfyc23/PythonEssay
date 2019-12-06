# -*- coding: utf-8 -*-
"""
Project: PythonEssay
Creator: DoubleThunder
Create time: 2019-12-06 17:08
Introduction: P 站下载
使用说明：> python pronhub_url.py "https://www.pornhub.com/view_video.php?viewkey=ph5c07b7ed1777b"

"""

import sys
import re
import time
import os
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


url_compile = r"(?x)https?://(?:(?:[^/]+\.)?(?P<host>pornhub\.(?:com|net))/(?:(?:view_video\.php|video/show)\?viewkey=|embed/)|(?:www\.)?thumbzilla\.com/video/)(?P<id>[\da-z]+)"


def get_pronhub_url(url):
    if not re.findall(url_compile, url):
        print('请输出正确的 P 站地址')
        return

    options = Options()
    options.add_argument('headless')
    options.add_argument("log-level=3")

    browser = Chrome(options=options, service_log_path=os.path.devnull)
    browser.get(url)

    time.sleep(2)  # 让子弹飞一会儿了

    key = re.findall(r"flashvars_\d{1,}", browser.page_source)[0]

    video_title = browser.find_element_by_class_name("inlineFree").text
    print("标题：{}".format(video_title))

    datas = browser.execute_script('return eval(arguments[0])', key)

    for md in datas['mediaDefinitions']:
        video_url = md['videoUrl']
        quality = md['quality']
        _format = md['format']
        if _format == "mp4":
            print("清晰度：{}P，视频地址：{}".format(quality, video_url))
    browser.quit()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("请输出 P 站视频地址链接")
        exit(-1)

    else:
        url = sys.argv[1]
        get_pronhub_url(url)

    # url = "https://www.pornhub.com/view_video.php?viewkey=ph5c07b7ed1777b"
    # get_pronhub_url(url)
