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
from assets import *

end_str = '\n素材取自网络，如有侵权请联系删除'

async def create_article(page,dialog):
    await page.wait_for_timeout(2000)
    input_container = await page.wait_for_selector("#root > div > div > div > div > div.publish-box > div.syl-editor") 
    container = await input_container.query_selector(':first-child')  
    await container.fill(dialog['content'])
    await page.wait_for_timeout(2000)
    add_pic = await page.wait_for_selector('#root > div > div > div > div > div.img-form-wrap > div.toolbar > div > div.toolbar-mount-node > div > div.syl-toolbar-tool.weitoutiao-image-plugin.static > span > button')
    await add_pic.click()
    await page.wait_for_timeout(2000)
    
    # 选择图片  
    page.on("filechooser", lambda file_chooser: file_chooser.set_files(dialog['imgs']))
    from_local = await page.wait_for_selector('body > div.byte-drawer-wrapper > div.byte-drawer.primary-drawer.mp-ic-img-drawer.is-first.slideRight-appear-done.slideRight-enter-done > div > div > div.byte-drawer-content.byte-drawer-content-nofooter > div > div.byte-tabs-content.byte-tabs-content-horizontal > div > div.byte-tabs-content-item.byte-tabs-content-item-active > div > div > div > div.btn-upload-scand.is-empty > div > button:nth-child(1) > div')
    await from_local.click()
    await page.wait_for_timeout(2000)

    ok_pic = await page.wait_for_selector('body > div.byte-drawer-wrapper > div.byte-drawer.primary-drawer.mp-ic-img-drawer.is-first.slideRight-appear-done.slideRight-enter-done > div > div > div.byte-drawer-content.byte-drawer-content-nofooter > div > div.byte-tabs-content.byte-tabs-content-horizontal > div > div.byte-tabs-content-item.byte-tabs-content-item-active > div > div > div > div.footer > div.confirm-btns > button.byte-btn.byte-btn-primary.byte-btn-size-large.byte-btn-shape-square')
    await ok_pic.click()
    await page.wait_for_timeout(2000)
    
    save_draft = await page.wait_for_selector('#root > div > div > div > div > div.footer-wrap > div > button.byte-btn.byte-btn-default.byte-btn-size-default.byte-btn-shape-square.save-draft')
    await save_draft.click()
    await page.wait_for_timeout(5000)

def handle_dialog(dialog):
    dialog.dismiss()

async def add_article(cookie_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                          chromium_sandbox=False,
                                          ignore_default_args=["--enable-automation"],
                                          channel="chrome"
                                          )
        context = await browser.new_context(
            storage_state=cookie_file,
            user_agent=const.UA["web"]
        )
        # context 禁止位置权限
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        # 发布微头条
        await page.goto("https://mp.toutiao.com/profile_v4/weitoutiao/publish")
        
        # --------------------------------开始发布流程-------------------------------------------
        await create_article(page)
        # ------------------------------------发布流程结束-------------------------------------------------------
        # 关掉浏览器
        await browser.close()

async def publish():
    cookie_list = find_cookie('jrrt_cookie')
    article_list = find_article()
    for cookie in cookie_list:
        try:
            await add_article(cookie)
        except Exception as e:
            print(e)

asyncio.run(publish())
            