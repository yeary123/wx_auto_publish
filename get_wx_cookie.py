# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/10 22:11
@Author  : superhero
@Email   : 838210720@qq.com
@File    : get_cookie.py
@IDE: PyCharm
"""

import asyncio
import os
from playwright.async_api import Playwright, async_playwright


class creator_wx():
    def __init__(self, email, timeout: int):
        """
        初始化
        :param email: Email邮箱
        :param timeout: 你要等待多久，单位秒
        """
        self.timeout = timeout * 1000
        self.email = email
        self.path = os.path.abspath('')
        self.desc = "cookie_%s.json" % email

        if not os.path.exists(os.path.join(self.path, "cookie")):
            os.makedirs(os.path.join(self.path, "cookie"))

    async def __cookie(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(channel="chrome", headless=False)

        context = await browser.new_context()

        page = await context.new_page()

        await page.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>false}});")

        await page.goto("https://mp.weixin.qq.com/")

        try:
            await page.wait_for_url("https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&*token=*", timeout=self.timeout)
            cookies = await context.cookies()
            cookie_txt = ''
            for i in cookies:
                cookie_txt += i.get('name') + '=' + i.get('value') + '; '
            try:
                cookie_txt.index("ua_id")
                print(self.email + " ——> 登录成功")
                # with open(os.path.join(self.path, "cookie", self.phone + ".txt"), mode="w") as f:
                #     f.write(cookie_txt)
                await context.storage_state(path=os.path.join(self.path, "cookie", self.desc))
            except ValueError:
                print(self.email + " ——> 登录失败，本次操作不保存cookie")
        except Exception as e:
            print(self.email + " ——> 登录失败，本次操作不保存cookie", e)
        finally:
            await page.close()
            await context.close()
            await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.__cookie(playwright)


def main():
    while True:
        email = input('请输入email\n输入"exit"将退出服务\n')
        if email == "exit":
            break
        else:
            app = creator_wx(email, 60)
            asyncio.run(app.main())


main()
