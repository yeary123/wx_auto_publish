import asyncio
import logging
import time
from playwright.async_api import Playwright, async_playwright
import os
import sys
sys.path.append(os.getcwd())
from base.config import conigs
from base.logs import config_log
import package_base

# 获取当前文件的完整路径  
current_file_path = __file__  
from playwright.sync_api import sync_playwright  

async def get_all_a_tags(page):  
    # 使用 evaluate 函数在浏览器上下文中执行 JavaScript  
    result = await page.evaluate("""() => {  
        const anchors = document.querySelectorAll('a');  
        const links_and_texts = [];  
        anchors.forEach(anchor => {  
            links_and_texts.push({  
                title: anchor.title || '',  
                href: anchor.href  
            });  
        });  
        return links_and_texts;  
    }""")  
    return result  


class xb():
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


class login_xb(xb):
    def __init__(self, timeout: int, cookie_file: str, dialog_file: str = None):
        super(login_xb, self).__init__()
        """
        初始化
        :param timeout: 你要等待多久，单位秒
        :param cookie_file: cookie文件路径
        """
        self.timeout = timeout * 1000
        self.cookie_file = cookie_file
        
    async def login(self) -> None:
        async with async_playwright() as playwright:
            browser = await self.playwright_init(playwright,True)
            context = await browser.new_context(storage_state=self.cookie_file, user_agent=self.ua["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://a.newrank.cn/trade/media/hotList")
            print("正在判断账号是否登录")
            try:
                avatar = await page.wait_for_selector('#__layout > div > header > div.nr-content.inner > div.right > div > div > span')
            except:
                package_base.delete_all_files('cookie')
                print("账号未登陆")
                return


            print("账号已登陆")

            # 选择阅读数前50
            selector = await page.wait_for_selector('#__layout > div > div.container > div > div.list-content > div.filter-box > div:nth-child(2) > div:nth-child(2)')
            await selector.click()
            read50 = await page.wait_for_selector('body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li:nth-child(2)')
            await read50.click()
            print('选择阅读数50标签')
            # 获取所有的 a 标签文字和链接  
            a_tags_data = await get_all_a_tags(page)  
            print('抓取其中的文章名和链接')
            # 将结果写入 txt 文件  
            package_base.write_to_txt(a_tags_data, 'xb_output.txt','weixin')  

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
    path = os.path.join(os.path.dirname(current_file_path) , find_path)
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
        app = login_xb(60, cookie_path)
        asyncio.run(app.main())


if __name__ == '__main__':
    run()