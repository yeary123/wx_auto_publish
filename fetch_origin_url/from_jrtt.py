from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到sys.path
from const import *
import asyncio
import package_base

base_url = "https://www.toutiao.com/?channel="
military_url = base_url + MILITARY
finance_url = base_url + FINANCE
tech_url = base_url + TECH
sports_url = base_url + SPORTS
history_url = base_url + HISTORY
food_url = base_url + FOOD
travel_url = base_url + TRAVEL
hot_url = base_url + HOT
entertainment_url = base_url + ENTERTAINMENT

async def scroll_page(page):
    await page.evaluate("""
        () => {
            window.scrollTo(0, document.body.scrollHeight);
        }
    """)

async def get_data(page,area_selector):
    # 进入xx频道
    area = await page.wait_for_selector(area_selector)
    await area.click()
    await page.wait_for_timeout(2000)
    for _ in range(5):
        await scroll_page(page)
        await page.wait_for_timeout(2000)
    elements = await page.query_selector_all('.feed-card-wrapper.feed-card-article-wrapper')
    datas = []
    for element in elements:
        article = await element.query_selector('a.title')
        href = await article.get_attribute('href')
        title = await article.get_attribute('aria-label')
        datas.append({'href':href,'title':title})
    return datas

async def deal(page,area):
    datas = await get_data(page,area.value)
    package_base.write_to_txt(datas,f'{area.name}.txt')


async def goto_page(area):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                        chromium_sandbox=False,
                                        ignore_default_args=["--enable-automation"],
                                        channel="chrome"
                                        )
        context = await browser.new_context(user_agent=const.UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        await page.goto("https://www.toutiao.com/")
        
        await deal(page,area)
        
        # 关掉浏览器
        await browser.close()
