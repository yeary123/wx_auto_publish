import asyncio
import logging
from moviepy.editor import *
from playwright.async_api import Playwright, async_playwright
sys.path.append(os.getcwd())
from base.logs import config_log
import post_article.get_wx_cookie as get_wx_cookie
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

class wx():
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


class login_wx(wx):
    def __init__(self, cookie_file: str):
        super(login_wx, self).__init__()
        self.cookie_file = cookie_file
        
    async def login(self) -> bool:
        async with async_playwright() as playwright:
            browser = await self.playwright_init(playwright,True)
            context = await browser.new_context(storage_state=self.cookie_file, user_agent=const.UA["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://mp.weixin.qq.com/")
            print("开始判断账号是否登录")
            if "token" not in page.url:
                # 删掉cookie文件
                try:
                    os.remove(self.cookie_file)
                except FileNotFoundError:
                    pass
                return False
            # 关掉浏览器
            await browser.close()
            return True


# 文件查找 path 绝对路径， file_type 文件类型
def find_file(path, file_type) -> list:
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

async def check_log_state():
    print("开始检查微信公众号账号登录情况")
    cookie_list = find_cookie('wx_cookie')
    # 没有cookie文件
    if len(cookie_list) == 0:
        print("未找到cookie文件，请先登录")
        await get_wx_cookie.main()
        cookie_list = find_cookie('wx_cookie')
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
                result = await login_wx(cookie_path).login()
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
        cookie_list = find_cookie('wx_cookie')
        if len(cookie_list) > 0:
            print("已有[%s]个账号成功登陆" % len(cookie_list))
        else:
            print("没有登录账号，程序退出")
            exit()

asyncio.run(check_log_state())