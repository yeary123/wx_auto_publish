import asyncio
import logging
from moviepy.editor import *
from playwright.async_api import Playwright, async_playwright
sys.path.append(os.getcwd())
from base.logs import config_log
import post_article.get_jrtt_cookie as get_jrtt_cookie
import const 
from assets import *

  
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

class jrtt():
    def __init__(self):
        config_log()
        self.title = ""
        self.ids = ""
        self.page = 0
        self.path = os.path.abspath('')

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


class login_jrtt(jrtt):
    def __init__(self, cookie_file: str):
        super(login_jrtt, self).__init__()
        self.cookie_file = cookie_file
        
    async def login(self) -> bool:
        async with async_playwright() as playwright:
            browser = await self.playwright_init(playwright,True)
            context = await browser.new_context(storage_state=self.cookie_file, user_agent=const.UA["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://www.toutiao.com/")
            print("开始判断账号是否登录")
            avatar = await page.query_selector("#root > div > div.toutiao-header > div.header-right.common-component-wrapper > div.user-icon > a")
            if avatar is None:
                # 删掉cookie文件
                try:
                    os.remove(self.cookie_file)
                except FileNotFoundError:
                    pass
                return False
            # 关掉浏览器
            await browser.close()
            return True

async def check_log_state():
    print("开始检查今日头条账号登录情况")
    cookie_list = find_cookie('jrtt_cookie')
    # 没有cookie文件
    if len(cookie_list) == 0:
        print("未找到cookie文件，请先登录")
        get_jrtt_cookie.main()
        cookie_list = find_cookie('jrtt_cookie')
        if len(cookie_list) > 0:
            print("已有[%s]个账号成功登陆" % len(cookie_list))
        else:
            print("没有登录账号，程序退出")
            exit()
    else:# 有cookie文件，查看登陆状态
        for index,cookie_path in enumerate(cookie_list):
            cookie_name: str = os.path.basename(cookie_path)
            author = cookie_name.split("_")[1][:-5]
            print("正在检查[%s]账号登录情况，当前序号[%s]" % (author, str(index)))
            try:
                result = await login_jrtt(cookie_path).login()
                if result == True:
                    print("账号[%s]登录成功" % author)
                else:
                    print("账号[%s]登录失败" % author)
                    continue
            except Exception as e:
                # 删掉cookie文件
                try:
                    os.remove(cookie_path)
                except FileNotFoundError:
                    pass
                print("账号[%s]登录失败" % author)
                continue
        cookie_list = find_cookie('jrtt_cookie')
        if len(cookie_list) > 0:
            print("已有[%s]个账号成功登陆" % len(cookie_list))
        else:
            print("没有登录账号，程序退出")
            exit()

# asyncio.run(check_log_state())