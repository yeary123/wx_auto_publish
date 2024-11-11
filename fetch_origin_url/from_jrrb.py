# 从今日热榜抓数据
from playwright.async_api import Playwright, async_playwright
import asyncio
from . import package_base
import sys
import os
sys.path.append(os.getcwd())
from const import *

async def fetch_news_from_site(url, output_filename, folder_name, get_child_elements_func, get_title_func):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context(user_agent=UA["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        await page.goto(url)
        print(f"开始从{url}获取新闻")
        
        # 等待网页加载完成（可根据需要调整）
        await page.wait_for_timeout(5000)
        
        # 调用传入的函数获取child_elements
        child_elements = await get_child_elements_func(page)
        
        datas = []
        for child in child_elements:
            await child.click()
            # 等待新页面加载（可根据需要调整）
            await page.wait_for_timeout(2000)
            # 假设新打开的页面是context中的最后一个
            news_page = context.pages[-1]
            
            # 获取页面链接
            href = await news_page.evaluate("window.location.href")
            
            # 调用传入的函数获取页面标题
            title = await get_title_func(news_page)

            # title和href都不能为空
            if href is None or href == "":
                continue
            if title is None or title == "":
                continue
            # 将数据添加到datas列表中
            datas.append({"title": title, "href": href})
        
        # 打印和保存数据
        print(datas)
        package_base.write_to_txt(datas, output_filename, second_folder_name=folder_name,max_num=MAX_NUM_PER_SEND)
        print(f"已从{url}获取[{len(datas)}]条新闻，放入文件夹：[{folder_name}]下，文件名为：[{output_filename}]")
        
        # 清理资源
        await context.close()
        await browser.close()

async def get_jrrb_elements(page):
    parent_element = await page.query_selector_all("#app > div.__layout-1uk59wc-e.n-layout.n-layout--static-positioned.fixed > div > div.n-scrollbar-container > div > main > div > div.n-card.__card-1uk59wc-m.n-card--bordered.card > div.n-card__content > div > ul")  # 使用网易的具体选择器
    child_elements = await parent_element[0].query_selector_all('li') if parent_element else []
    return child_elements

# 使用示例
async def from_36ke():
    url = "https://hot.imsyy.top/#/list?type=36kr&page=1"
    output_filename = '36ke.txt'
    folder_name = TECH
    get_child_elements = get_jrrb_elements

    async def get_36ke_title(news_page):
        title_element = None
        # 获取页面标题
        try:
            title_element = await news_page.wait_for_selector('#app > div > div.box-kr-article-new-y > div > div.kr-layout-main.clearfloat > div.main-right > div > div > div > div.article-detail-wrapper-box > div > div.article-left-container > div.article-content > div > div > div:nth-child(1) > div > h1',timeout=5000)
        except Exception as e:
            print(f'36ke->title selector:{e}')
        
        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements ,get_36ke_title)

async def from_netease():
    url = "https://hot.imsyy.top/#/list?type=netease-news"
    output_filename = 'net_ease.txt'
    folder_name = HOT
    get_child_elements = get_jrrb_elements
    async def get_netease_title(news_page):
        title_element = None
        try:
            title_element = await news_page.wait_for_selector('#contain > div.post_main > h1',timeout=5000)
        except Exception as e:
            print(f'netease->title selector:{e}')

        try:
            title_element = await news_page.wait_for_selector('#container > div.post_main > h1',timeout=5000)
        except Exception as e:
            print(f'netease->title selector:{e}')
        
        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements,get_netease_title)

async def from_shaoshupai():
    url = "https://hot.imsyy.top/#/list?type=sspai&page=1"
    output_filename = 'shaoshupai.txt'
    folder_name = TECH
    get_child_elements = get_jrrb_elements
    async def get_title(news_page):
        title_element = None
        try:
            title_element = await news_page.wait_for_selector('#app > div.postPage.article-wrapper > div.article-detail > article > div.article-header.important-header > div.content > div.article-info > div.title.text_ellipsis4',timeout=5000)
        except Exception as e:
            print(f'少数派->title selector:{e}')
        if title_element is None:
            try:
                title_element = await news_page.wait_for_selector('#article-title',timeout=5000)
            except Exception as e:
                print(f'少数派->title selector:{e}')

        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements,get_title)

async def from_itzhijia():
    url = "https://hot.imsyy.top/#/list?type=ithome&page=1"
    output_filename = 'it之家.txt'
    folder_name = TECH
    get_child_elements = get_jrrb_elements
    async def get_title(news_page):
        title_element = None
        try:
            title_element = await news_page.wait_for_selector('#dt > div.fl.content > h1',timeout=5000)
        except Exception as e:
            print(f'it之家->title selector:{e}')

        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements,get_title)

async def from_pengpai():
    url = "https://hot.imsyy.top/#/list?type=thepaper&page=1"
    output_filename = 'pengpai.txt'
    folder_name = HOT
    get_child_elements = get_jrrb_elements
    async def get_title(news_page):
        title_element = None
        try:
            title_element = await news_page.wait_for_selector('#__next > main > div.index_container__ETYBL.index_normalContentWrap__q1ikz > div.index_leftcontent__lACdC.index_leftClass__q6ZdE > div.index_wrap__e0qtz > div > h1',timeout=5000)
        except Exception as e:
            print(f'澎湃->title selector:{e}')

        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements,get_title)

#不用它，内容太专业了
async def from_juejin():
    url = "https://hot.imsyy.top/#/list?type=juejin&page=1"
    output_filename = 'juejin.txt'
    folder_name = TECH
    get_child_elements = get_jrrb_elements
    async def get_title(news_page):
        title_element = None
        try:
            title_element = await news_page.wait_for_selector('#juejin > div.view-container > main > div > div.main-area.article-area > article > h1',timeout=5000)
        except Exception as e:
            print(f'掘金->title selector:{e}')

        if title_element is None:
            return ''
        else:
            return await title_element.inner_text()

    await fetch_news_from_site(url, output_filename, folder_name, get_child_elements,get_title)

# asyncio.run(from_36ke())