from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到sys.path
from const import *
import asyncio
from fetch_origin_url.package_base import *

base_url = "https://www.toutiao.com/?channel="
# 获取当前文件的完整路径  
current_file_path = __file__  
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

async def goto_page(area):
    cookie_list = find_file("cookie", "json")
    #寻找文件中包含 ‘板栗’ 字符的文件
    for i in cookie_list:
        if i.find('板栗') != -1:
            cookie_file = i
            break
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                        chromium_sandbox=False,
                                        ignore_default_args=["--enable-automation"],
                                        channel="chrome"
                                        )
        context = await browser.new_context(storage_state=cookie_file, user_agent=UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        url = base_url + area
        await page.goto(url)
        await page.wait_for_timeout(5000)
        avatar = await page.query_selector('#root > div > div.toutiao-header > div.header-right.common-component-wrapper > div.user-icon > a > img')
        if avatar is None:
            print("未登陆成功，无法抓取数据")
        else:
            await deal(page,area)
        
        # 关掉浏览器
        await browser.close()

async def from_jrtt(categories):
    tasks = [goto_page(area) for area in categories]
    for task in tasks:
        await task 

# asyncio.run(from_jrtt([HISTORY]))