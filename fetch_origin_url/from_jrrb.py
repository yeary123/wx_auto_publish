# 从今日热榜抓数据
from playwright.async_api import Playwright, async_playwright
import asyncio
import package_base

# 获取网易热搜
async def from_wy():
    # 打开网页
    ua = {
            "web": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
                   "Safari/537.36",
            "app": "com.ss.android.ugc.aweme/110101 (Linux; U; Android 5.1.1; zh_CN; MI 9; Build/NMF26X; "
                   "Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)"
        }
    async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(channel="chrome", headless=False)
            context = await browser.new_context(user_agent=ua["web"])
            page = await context.new_page()
            await page.add_init_script(path="stealth.min.js")
            await page.goto("https://hot.imsyy.top/#/list?type=netease-news")
            # 等待网页加载完成
            await page.wait_for_timeout(1000)
            # 获取网页中的list内容
            parent_element = await page.query_selector_all("#app > div.__layout-1uk59wc-e.n-layout.n-layout--static-positioned.fixed > div > div.n-scrollbar-container > div > main > div > div.n-card.__card-1uk59wc-m.n-card--bordered.card > div.n-card__content > div > ul")
            # 获取parent_element的所有子元素
            child_elements = await parent_element[0].query_selector_all('li') if parent_element else []
            titles = []
            for child in child_elements:
                # 获取child的某个 class = n-text __text-1uk59wc-d title 的元素的文本
                title_element = await child.query_selector('.n-text.__text-1uk59wc-d.title')
                title = await title_element.inner_text()
                titles.append(title)
                await child.click()
                await page.wait_for_timeout(1000)
            # 获取所有标签页的url
            pages = context.pages
            urls = [await page.evaluate("window.location.href") for page in pages]
            
            # 删除第一个元素
            urls.remove(urls[0])
            
            # title 和 url 一一对应放进list里，字段名 title 和 href
            data = [{"title": t, "href": u} for t, u in zip(titles, urls)]

            package_base.write_to_txt(data, 'net_ease.txt')
            print(urls)
            # 关闭网页
            await context.close()
            await browser.close()

asyncio.run(from_wy())