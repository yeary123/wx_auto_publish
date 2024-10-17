import asyncio
import hashlib
import logging
import random
import re
import time

import cv2
import pandas as pd
import requests
from PIL import Image
from apscheduler.schedulers.blocking import BlockingScheduler
# from ffmpy import FFmpeg
from moviepy.editor import *
from playwright.async_api import Playwright, async_playwright
from config import conigs
from logs import config_log
from tqdm import tqdm
from datetime import datetime
from PIL import Image  
import pyperclip
import io  
  
def image_to_clipboard(image_path):  
    img = Image.open('/Users/liqian/Documents/wireshark.jpeg')
    image_data = img.tobytes()
    pyperclip.copy(image_data)

  
# 使用函数  
image_to_clipboard('/path/to/your/image.png')
def delete_all_files(folder_path):
    # 获取文件夹中所有文件的列表
    try:
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            # 判断是否为文件
            if os.path.isfile(file_path):
                # 删除文件
                os.remove(file_path)
    except:
        print("delete_all_files except")

class wx():
    def __init__(self):
        config_log()
        self.title = ""
        self.ids = ""
        self.page = 0
        self.path = os.path.abspath('')
        self.ua = {
            "web": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
                   "Safari/537.36",
            "app": "com.ss.android.ugc.aweme/110101 (Linux; U; Android 5.1.1; zh_CN; MI 9; Build/NMF26X; "
                   "Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)"
        }

    async def playwright_init(self, p: Playwright, headless=None):
        """
        初始化playwright
        """
        if headless is None:
            headless = False

        browser = await p.chromium.launch(headless=headless,
                                          chromium_sandbox=False,
                                          ignore_default_args=["--enable-automation"],
                                          channel="chrome"
                                          )
        return browser


class login_wx(wx):
    def __init__(self, timeout: int, cookie_file: str, dialog_file: str = None):
        super(login_wx, self).__init__()
        """
        初始化
        :param timeout: 你要等待多久，单位秒
        :param cookie_file: cookie文件路径
        """
        self.timeout = timeout * 1000
        self.cookie_file = cookie_file
        self.dialog_file = dialog_file
        self.dialog = {
            'title':'1211212',
            'author':'222',
            'content':'fffegewqgeq',
        }
        
    async def login(self) -> None:
        image_to_clipboard('')
        async with async_playwright() as playwright:
            browser = await self.playwright_init(playwright,False)
            context = await browser.new_context(storage_state=self.cookie_file, user_agent=self.ua["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://mp.weixin.qq.com/")
            print("正在判断账号是否登录")
            if "token" not in page.url:
                print("账号未登录")
                logging.info("账号未登录")
                return
            print("账号已登录")
            # 使用text()选择器查找包含"图文消息"文字的div元素  
            element = await page.query_selector('//*[@id="app"]/div[2]/div[3]/div[2]/div/div[2]')  
            await element.click()

            # 监听新页面打开事件（异步方式）  
            async with page.expect_event('popup') as event_info:  
                new_page = await event_info.value  # 在这里，value 是可用的，因为它是异步上下文管理器的结果  

            # 填写标题
            await new_page.click('//*[@id="title"]')  # 使用正确的ID选择器  
            await new_page.keyboard.type(self.dialog['title'])
            # 填写作者
            await new_page.keyboard.press('Tab')  
            await new_page.keyboard.type(self.dialog['author'])
            # 填写正文
            await new_page.keyboard.press('Tab')  
            img_data = pyperclip.paste()
            image = io.BytesIO(img_data)  
            await new_page.keyboard.type(image)
            await new_page.keyboard.type(self.dialog['content'])
            # 选择第一张图片做封面
            pic = await new_page.query_selector('//*[@id="js_cover_area"]/div[1]')
            await pic.hover()
            new_page.wait_for_timeout(500)  
            pick_from_article = await new_page.query_selector('//*[@id="js_cover_null"]/ul/li[1]/a')
            await pick_from_article.click()
            new_page.wait_for_timeout(500)  
            first_pic = await new_page.query_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[2]/div[1]/div/ul')
            await first_pic.click()
            new_page.wait_for_timeout(500)  
            next_btn = await new_page.query_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div[1]/button')
            await next_btn.click()
            new_page.wait_for_timeout(500)
            finish_btn = await new_page.query_selector('//*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div[2]/button')
            await finish_btn.click()
            new_page.wait_for_timeout(500)
            publish_btn = await new_page.query_selector('//*[@id="js_send"]/button')
            await publish_btn.click()
            new_page.wait_for_timeout(500)
            publish_again = await new_page.query_selector('//*[@id="vue_app"]/div[2]/div[1]/div[1]/div/div[3]/div/div/div[1]/button')
            await publish_again.click()
            new_page.wait_for_timeout(500)
            publish_3 = await new_page.query_selector('//*[@id="vue_app"]/div[2]/div[2]/div[1]/div/div[3]/div/div[1]/button')
            await publish_3.click()
            new_page.wait_for_timeout(500)

            time.sleep(10)

            
    async def main(self):
        await self.login()


def find_file(find_path, file_type) -> list:
    """
    寻找文件
    :param find_path: 子路径
    :param file_type: 文件类型
    :return:
    """
    path = os.path.join(os.path.abspath(""), find_path)
    if not os.path.exists(path):
        os.makedirs(path)
    data_list = []
    for root, dirs, files in os.walk(path):
        if root != path:
            break
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.find(file_type) != -1:
                data_list.append(file_path)
    return data_list


def run():
    cookie_list = find_file("cookie", "json")
    x = 0
    for cookie_path in cookie_list:
        x += 1
        cookie_name: str = os.path.basename(cookie_path)
        print("正在使用[%s]发布作品，当前账号排序[%s]" % (cookie_name.split("_")[1][:-5], str(x)))
        app = login_wx(60, cookie_path)
        asyncio.run(app.main())


if __name__ == '__main__':
    run()