from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到sys.path
from const import *
import asyncio
from . import package_base
from .package_base import *

base_url = "https://www.toutiao.com/?channel="

async def scroll_page(page):
    await page.evaluate("""
        () => {
            window.scrollTo(0, document.body.scrollHeight);
        }
    """)

async def get_data(page):
    # for _ in range(5):
    #     await scroll_page(page)
    #     await page.wait_for_timeout(2000)
    elements = await page.query_selector_all('.feed-card-wrapper.feed-card-article-wrapper')
    datas = []
    for element in elements:
        article = await element.query_selector('a.title')
        href = await article.get_attribute('href')
        title = await article.get_attribute('aria-label')
        datas.append({'href':href,'title':title})
    return datas

async def deal(page,area):
    datas = await get_data(page)
    write_to_txt(datas,f'toutiao_{area}.txt',second_folder_name = area,max_num = MAX_NUM_PER_SEND)


async def goto_page(area):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                        chromium_sandbox=False,
                                        ignore_default_args=["--enable-automation"],
                                        channel="chrome"
                                        )
        context = await browser.new_context(user_agent=UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        url = base_url + area
        await page.goto(url)
        await page.wait_for_timeout(5000)
        await deal(page,area)
        
        # 关掉浏览器
        await browser.close()

async def from_jrtt():
    categories = [MILITARY, FINANCE, TECH, SPORTS, HISTORY, FOOD, TRAVEL, HOT, ENTERTAINMENT]
    tasks = [goto_page(area) for area in categories]
    await asyncio.gather(*tasks)
    
# asyncio.run(main())