from playwright.async_api import Playwright, async_playwright
import asyncio
import time
import os
import sys
sys.path.append(os.getcwd())
from base.logs import config_log
import post_article.get_jrtt_cookie as get_jrtt_cookie
import post_article.check_login_jrtt as check_login_jrtt
import logging
import const

async def add_article(cookie_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                          chromium_sandbox=False,
                                          ignore_default_args=["--enable-automation"],
                                          channel="chrome"
                                          )
        context = await browser.new_context(storage_state=cookie_file, user_agent=const.UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        # 发布微头条
        await page.goto("https://mp.toutiao.com/profile_v4/weitoutiao/publish")
        
        # --------------------------------开始发布流程-------------------------------------------
        page.on("dialog", lambda dialog: dialog.dismiss())
        input_container = await page.wait_for_selector("#root > div > div > div > div > div.publish-box > div.syl-editor > div.ProseMirror")
        await input_container.click()
        await page.keyboard.type('测试内容')
        await page.wait_for_timeout(10000)
        # ------------------------------------发布流程结束-------------------------------------------------------
        # 关掉浏览器
        await browser.close()

async def publish():
    cookie_list = check_login_jrtt.find_cookie()
    for cookie in cookie_list:
        try:
            await add_article(cookie)
        except Exception as e:
            print(e)

asyncio.run(publish())
            